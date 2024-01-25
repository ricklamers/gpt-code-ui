import { useRef, useState } from "react";

import FileUploadIcon from "@mui/icons-material/FileUpload";
import SendIcon from "@mui/icons-material/Send";
import TextareaAutosize from "react-textarea-autosize";
import Config from "../config";
import "./Input.css";

export default function Input(props: { onSendMessage: any, onStartUpload: any, onCompletedUpload: any }) {

  let fileInputRef = useRef<HTMLInputElement>(null);
  let [inputIsFocused, setInputIsFocused] = useState<boolean>(false);
  let [userInput, setUserInput] = useState<string>("");

  const handleInputFocus = () => {
    setInputIsFocused(true);
  };

  const handleInputBlur = () => {
    setInputIsFocused(false);
  };

  const handleUpload = (e: any) => {
    e.preventDefault();
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: any) => {
    if (e.target.files.length > 0) {
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
    props.onSendMessage(userInput);
    setUserInput("");
  }

  const handleInputChange = (e: any) => {
    setUserInput(e.target.value);
  };

  const handleKeyDown = (e: any) => {
    if (e.key === "Enter" && e.shiftKey === false) {
        e.preventDefault();
        handleSendMessage();
    }
  };

  return (
    <div className="input-parent">
      <div className={"input-holder " + (inputIsFocused ? "focused" : "")}>
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
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onChange={handleInputChange}
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
