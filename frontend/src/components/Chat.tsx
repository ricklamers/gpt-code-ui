import "./Chat.css";

import VoiceChatIcon from "@mui/icons-material/VoiceChat";
import PersonIcon from "@mui/icons-material/Person";
import TerminalIcon from '@mui/icons-material/Terminal';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import { MessageDict } from "../App";

import remarkGfm from 'remark-gfm';
import SyntaxHighlighter from "react-syntax-highlighter";
import { RefObject } from "react";
import ReactMarkdown from 'react-markdown';

function Message(props: {
  text: string;
  role: string;
  type: string;
  showLoader?: boolean;
}) {
  let { text, role } = props;

  const isMarkdown = (input: string) => {
    const mdRegex = /\[.*\]\(.*\)|\*\*.*\*\*|__.*__|\#.*|\!\[.*\]\(.*\)|`.*`|\- .*|\|.*\|/g;
    return mdRegex.test(input);
  };

  let ICONS = {
    "upload": <FileUploadIcon />,
    "generator":  <VoiceChatIcon />,
    "system": <TerminalIcon />,
    "user": <PersonIcon />,
  };

  return (
    <div className={"message " + role}>
      <div className="avatar-holder">
        <div className="avatar">
          { ICONS[role as keyof typeof ICONS] }
        </div>
      </div>
      <div className="message-body">
        {props.type == "message" &&
          (props.showLoader ? (
            <div>
              {text} {props.showLoader ? <div className="loader"></div> : null}
            </div>
          ) : (
            isMarkdown(text) ? 
              <ReactMarkdown
              children={text}
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
            <div className="cell-output" dangerouslySetInnerHTML={{ __html: text }}></div>
          ))}

        {(props.type == "message_raw") &&
          (props.showLoader ? (
            <div>
              {text} {props.showLoader ? <div className="loader"></div> : null}
            </div>
          ) : (
            <div className="cell-output" dangerouslySetInnerHTML={{ __html: text }}></div>
          ))}
        
        {props.type == "image/png" &&
          <div className="cell-output-image" dangerouslySetInnerHTML={{ __html: `<img src='data:image/png;base64,${text}' />` }}></div>
        }
        {props.type == "image/jpeg" &&
          <div className="cell-output-image" dangerouslySetInnerHTML={{ __html: `<img src='data:image/jpeg;base64,${text}' />` }}></div>
        }
      </div>
    </div>
  );
}


export enum WaitingStates {
  GeneratingCode = "Generating code",
  RunningCode = "Running code",
  UploadingFile = "Uploading file",
  Idle = "Idle",
}

export default function Chat(props: {
  waitingForSystem: WaitingStates;
  chatScrollRef: RefObject<HTMLDivElement>;
  messages: Array<MessageDict>;
}) {
  return (
    <>
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
            type="message"
            showLoader={true}
          />
        ) : null}
      </div>
    </>
  );
}
