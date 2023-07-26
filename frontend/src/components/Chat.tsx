import "./Chat.css";

import VoiceChatIcon from "@mui/icons-material/VoiceChat";
import PersonIcon from "@mui/icons-material/Person";
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
  }

  return (
    <div className={"message " + (role == "system" ? "system" : "user")}>
      <div className="avatar-holder">
        <div className="avatar">
          {role == "system" ? <VoiceChatIcon /> : <PersonIcon />}
        </div>
      </div>
      <div className="message-body">
        {props.type == "code" && (
          <div>
            I generated the following code:
            <SyntaxHighlighter wrapLongLines={true} language="python">
              {text}
            </SyntaxHighlighter>
          </div>
        )}

        {["message", "message_status"].indexOf(props.type) !== -1 &&
          (props.showLoader ? (
            <div>
              {text} {props.showLoader ? <div className="loader"></div> : null}
            </div>
          ) : (
            isMarkdown(text) ? 
            <ReactMarkdown
            children={text}
            remarkPlugins={[remarkGfm]}
            /> :
            <div className="cell-output" dangerouslySetInnerHTML={{ __html: text }}></div>
          ))}

        {props.type == "message_error" &&
          (props.showLoader ? (
            <div>
              {text} {props.showLoader ? <div className="loader"></div> : null}
            </div>
          ) : (
            <div>
              Execution Error:
              <SyntaxHighlighter
                {...props}
                children={text}
                wrapLongLines={true}
                language={"python"}
                PreTag="div"
              />
            </div>
          ))}

        {props.type == "message_raw" &&
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
