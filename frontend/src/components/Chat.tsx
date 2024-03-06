import "./Chat.css";

import VoiceChatIcon from "@mui/icons-material/VoiceChat";
import PersonIcon from "@mui/icons-material/Person";
import TerminalIcon from '@mui/icons-material/Terminal';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import { MessageDict } from "../App";

import { Resizable } from 're-resizable';
import remarkGfm from 'remark-gfm';
import SyntaxHighlighter from "react-syntax-highlighter";
import React, { RefObject, useRef, useEffect } from "react";
import ReactMarkdown from 'react-markdown';


function Message_Loader(props: { text: string; }) {
  return (
    <div>
      {props.text}
      <div className="loader" />
    </div>
  );
}


function Message_Generic(props: { text: string; }) {
  const isMarkdown = (input: string) => {
    const mdRegex = /\[.*\]\(.*\)|\*\*.*\*\*|__.*__|\#.*|\!\[.*\]\(.*\)|`.*`|\- .*|\|.*\|/g;
    return mdRegex.test(input);
  };

  return (
      isMarkdown(props.text) ?
        <ReactMarkdown
        children={props.text}
        remarkPlugins={[remarkGfm]}
        components={{
          code({node, inline, className, children, style, ...props}) {
            const match = /language-(\w+)/.exec(className || '')
            return !inline ? (
              <SyntaxHighlighter
                {...props}
                children={String(children).replace(/\n$/, '')}
                wrapLongLines={true}
                language={match ? match[1] : "python"}
                PreTag="div"
              />
            ) : (
              <code {...props} className={className}>
                {children}
              </code>
            )
          }
        }}
      />
    :
      <div className="cell-output" dangerouslySetInnerHTML={{ __html: props.text }}></div>
  );
}


function Message_Error(props: { text: string; }) {
  return (
    <div>
      Execution Error:
      <SyntaxHighlighter
        {...props}
        children={props.text}
        wrapLongLines={true}
        language={"python"}
        PreTag="div"
      />
    </div>
  );
}


function Message_Resizable_Image(component: React.ReactElement, initial_height: string | number = 'auto', lockAspectRatio = true) {
  return (
    <div className="cell-output-image">
       <Resizable
          defaultSize={{ width: 600, height: initial_height }}
          enable={{ top: false, right: true, bottom: true, left: false, topRight: false, bottomRight: true, bottomLeft: false, topLeft: false }}
          handleStyles={{
            bottomRight: {
              marginTop: -9,
              marginLeft: -9,
              top: "100%",
              left: "100%",
              cursor: "nwse-resize",
              border: "2px dashed #999",
              borderLeft: "none",
              borderTop: "none",
              borderColor: "rgb(15, 105, 175)",
              width: 15,
              height: 15,
              boxSizing: "border-box",
              zIndex: 1
            },
          }}
          lockAspectRatio={ lockAspectRatio }
        >
          { component }
      </Resizable>
    </div>
  );
}


function Message_PNG(props: { text: string; }) {
  const component = <img src={`data:image/png;base64,${props.text}`} style={{ width: "100%", height: "100%", objectFit: "contain" }}/>;
  return Message_Resizable_Image( component );
}


function Message_JPEG(props: { text: string; }) {
  const component = <img src={`data:image/jpeg;base64,${props.text}`} style={{ width: "100%", height: "100%", objectFit: "contain" }}/>;
  return Message_Resizable_Image( component );
}


function Message_SVG(props: { text: string; }) {
  const component = <img src={`data:image/svg+xml;utf8,${encodeURIComponent(props.text)}`} style={{ width: "100%", height: "100%", objectFit: "contain" }}/>;
  return Message_Resizable_Image( component );
}


function Message_HTML(props: { text: string; }) {
  return <div className="cell-output" dangerouslySetInnerHTML={{ __html: `${props.text}` }} />
}


function Message_3dmol(props: { text: string; }) {
  const ref = useRef<HTMLDivElement>(null);
  const found = props.text.match(/3dmolviewer_\d*/);

  let text = (props.text
    .replace(/(viewer_\d+)(\.setSize.*$)/, '$1.resize(); //$2')
    .replace('https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js', './assets/3Dmol-min.js')
    .replace('\);\n<\/script>', `\).then( function() {
      const viewer = document.getElementById("${found}");
      viewer.style.width = "100%";
      viewer.style.height = "100%";
    }).catch( function(err) {
        const viewer = document.getElementById("${found}");
        const textnode = document.createTextNode(\`Execution Error:\n\${err}\`);
        viewer.parentElement.insertBefore(textnode, viewer);
        }
      );\n<\/script>`
    )
  );

  useEffect(() => {
    const node = document.createRange().createContextualFragment(text);
    if (ref.current) {
      ref.current.appendChild(node);
    }
  }, [ref]);

  const component = <div ref={ref} style={{ width: "100%", height: "100%", objectFit: "contain" }} />;
  return Message_Resizable_Image(component, '400px', false);
}


function Message(props: {
  text: string;
  role: string;
  type: string;
  showLoader?: boolean;
}) {
  let ICONS = {
    "upload": <FileUploadIcon />,
    "generator": <VoiceChatIcon />,
    "system": <TerminalIcon />,
    "user": <PersonIcon />,
  };

  const Message_Types = {
    "image/png": Message_PNG,
    "image/jpeg": Message_JPEG,
    "image/svg+xml": Message_SVG,
    "text/html": Message_HTML,
    "application/3dmoljs_load.v0": Message_3dmol,
    "message_error": Message_Error,
    "message_raw": Message_HTML,
    "message_status": Message_HTML,
    "message_loader": Message_Loader,
    "message": Message_Generic,
  };

  const Message_Type = Message_Types[props.type as keyof typeof Message_Types] || Message_Generic;

  return (
    <div className={"message " + props.role}>
      <div className="avatar-holder">
        <div className="avatar">
          { ICONS[props.role as keyof typeof ICONS] }
        </div>
      </div>
      <div className="message-body">
        <Message_Type text={props.text} />
      </div>
    </div>
  );
}


export enum WaitingStates {
  SessionTimeout = "Session timeout. Please reload the page.",
  WaitingForKernel = "Waiting for kernel connection",
  GeneratingCode = "Generating code",
  RunningCode = "Running code",
  UploadingFile = "Uploading file",
  Idle = "Ready",
}

export default function Chat(props: {
  waitingForSystem: WaitingStates;
  chatScrollRef: RefObject<HTMLDivElement>;
  messages: Array<MessageDict>;
}) {
  return (
    <div className="chat-messages" ref={props.chatScrollRef}>
      {props.messages.map((message, index) => {
        return (
          <Message
            key={index}
            text={message.text}
            role={message.role}
            type={message.type}
          />
        );
      })}
      {props.waitingForSystem != WaitingStates.Idle ? (
        <Message
          text={props.waitingForSystem}
          role="system"
          type="message_loader"
          showLoader={true}
        />
      ) : null}
    </div>
  );
}
