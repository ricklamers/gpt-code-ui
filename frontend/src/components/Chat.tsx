import "./Chat.css";

import VoiceChatIcon from "@mui/icons-material/VoiceChat";
import PersonIcon from "@mui/icons-material/Person";
import { MessageDict } from "../App";

import SyntaxHighlighter from "react-syntax-highlighter";
import { RefObject } from "react";

function Message(props: {
  text: string;
  role: string;
  kind: string;
  showLoader?: boolean;
}) {
  let { text, role } = props;

  return (
    <div className={"message " + (role == "system" ? "system" : "user")}>
      <div className="avatar-holder">
        <div className="avatar">
          {role == "system" ? <VoiceChatIcon /> : <PersonIcon />}
        </div>
      </div>
      <div className="message-body">
        {props.kind == "code" && (
          <div>
            I generated the following code:
            <SyntaxHighlighter wrapLongLines={true} language="python">
              {text}
            </SyntaxHighlighter>
          </div>
        )}

        {props.kind != "code" &&
          (props.showLoader ? (
            <div>
              {text} {props.showLoader ? <div className="loader"></div> : null}
            </div>
          ) : (
            <div className="cell-output" dangerouslySetInnerHTML={{ __html: text }}></div>
          ))}
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
              kind={message.kind}
            />
          );
        })}
        {props.waitingForSystem != WaitingStates.Idle ? (
          <Message
            text={props.waitingForSystem}
            role="system"
            kind="text"
            showLoader={true}
          />
        ) : null}
      </div>
    </>
  );
}
