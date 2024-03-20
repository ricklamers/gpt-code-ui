import { useRef, useState, KeyboardEvent, MouseEvent, ChangeEvent } from "react";

import FileUploadIcon from "@mui/icons-material/FileUpload";
import SendIcon from "@mui/icons-material/Send";
import TextareaAutosize from "react-textarea-autosize";
import Config from "../config";
import Foundry from "./Foundry";
import "./Input.css";
import { MessageDict } from "../App"


export default function Input(props: {
  Messages: MessageDict[],
  onSendMessage: (msg: string) => void,
  onStartUpload: (filename: string) => void,
  onCompletedUpload: (msg: string) => void,
  onSelectFoundryDataset: (name: string) => void; }
) {

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [inputIsFocused, setInputIsFocused] = useState<boolean>(false);
  const [userInput, setUserInput] = useState<string>('');
  const [messageReplay, setMessageReplay] = useState(0);

  const handleUpload = (e: MouseEvent) => {
    e.preventDefault();
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files != null && e.target.files.length > 0) {
      const file = e.target.files[0];

      // Create a new FormData instance
      const formData = new FormData();

      // Append the file to the form data
      formData.append("file", file);

      props.onStartUpload(file.name);

      try {
        const response = await fetch(Config.WEB_ADDRESS + "/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const json = await response.json();
        props.onCompletedUpload(json["message"]);

      } catch (error) {
        console.error("Error:", error);
      }
    }
  };


  const handleSendMessage = async () => {
    setMessageReplay(0);
    props.onSendMessage(userInput);
    setUserInput("");
  }

  const handleArrow = async (dir: number) => {
    let newMessage = messageReplay;
    while (newMessage + dir < 1 && newMessage + dir > -props.Messages.length) {
      newMessage = newMessage + dir;
      if (newMessage === 0) {
        setUserInput("");
        setMessageReplay(newMessage);
        break;
      } else if (props.Messages[props.Messages.length + newMessage].role === 'user') {
        setUserInput(props.Messages[props.Messages.length + newMessage].text);
        setMessageReplay(newMessage);
        break;
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && e.shiftKey === false) {
      e.preventDefault();
      handleSendMessage();
    } else if (e.key === 'ArrowUp' && e.altKey === true) {
      e.preventDefault();
      handleArrow(-1);
    } else if (e.key === 'ArrowDown' && e.altKey === true) {
      e.preventDefault();
      handleArrow(1);
    }
  };

  return (
    <div className="input-parent">
      <div className={"input-holder " + (inputIsFocused ? "focused" : "")}>

        <form className="file-open">
          <Foundry
            onSelectFoundryDataset = { props.onSelectFoundryDataset }
          />
        </form>

        <form className="file-upload">
          <input
            onChange={handleFileChange}
            ref={fileInputRef}
            style={{ display: "none" }}
            type="file"
          />
          <button type="button" onClick={handleUpload}>
            <FileUploadIcon />
          </button>
        </form>

        <TextareaAutosize
          onFocus={ () => setInputIsFocused(true) }
          onBlur={ () => setInputIsFocused(false) }
          onChange={ (e) => setUserInput(e.target.value) }
          onKeyDown={handleKeyDown}
          value={userInput}
          rows={1}
          placeholder="Send a message"
        />

        <button className="send" onClick={handleSendMessage}>
          <SendIcon />
        </button>

      </div>
    </div>
  );
}
