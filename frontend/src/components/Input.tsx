import { useRef, useState, KeyboardEvent, MouseEvent, ChangeEvent } from "react";

import FormControl from '@mui/material/FormControl';
import FileUploadIcon from "@mui/icons-material/FileUpload";
import FileOpenIcon from '@mui/icons-material/FileOpen';
import SendIcon from "@mui/icons-material/Send";
import Alert from '@mui/material/Alert';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import TextField from '@mui/material/TextField';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import TextareaAutosize from "react-textarea-autosize";
import Config from "../config";
import "./Input.css";
import { MessageDict } from "../App"


export default function Input(props: {
  Messages: MessageDict[],
  onSendMessage: (msg: string) => void,
  onStartUpload: (filename: string) => void,
  onCompletedUpload: (msg: string) => void,
  foundryFolder: string | undefined,
  onSelectFoundryFolder: (folder: string) => void,
  foundryAvailableDatasets: { name: string; dataset_rid: string; }[] | undefined;
  onSelectFoundryDataset: (name: string) => void; }
) {

  let fileInputRef = useRef<HTMLInputElement>(null);
  let [inputIsFocused, setInputIsFocused] = useState<boolean>(false);
  let [userInput, setUserInput] = useState<string>('');
  let [foundryDialogOpen, setFoundryDialogOpen] = useState(false);
  let [messageReplay, setMessageReplay] = useState(0);

  const handleFoundryDialogClose = (value: string) => {
    setFoundryDialogOpen(false);
    if (value != '') {
      props.onSelectFoundryDataset(value);
    }
  };

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
          <button type="button" onClick={ () => setFoundryDialogOpen(true) }>
            <FileOpenIcon />
          </button>
        </form>

        <Dialog open={foundryDialogOpen} onClose={() => handleFoundryDialogClose('') } fullWidth maxWidth="sm">
          <DialogTitle>Select Foundry Dataset</DialogTitle>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column' }}>
          <FormControl fullWidth>
            <TextField
              margin="dense"
              id="foundry-folder"
              label="Folder (RID or Path))"
              value={props.foundryFolder}
              onChange={e => { props.onSelectFoundryFolder(e.target.value); }}
            />
          </FormControl>
            {props.foundryAvailableDatasets != undefined && props.foundryAvailableDatasets.length > 0 &&
              <List sx={{ pt: 0 }}>
                {props.foundryAvailableDatasets.map((dataset) => (
                  <ListItem disableGutters key={dataset.dataset_rid}>
                    <ListItemButton onClick={() => handleFoundryDialogClose(dataset.dataset_rid)}>
                      <ListItemAvatar>
                        <Avatar>
                          <FileOpenIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText primary={dataset.name} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            }
            {props.foundryAvailableDatasets != undefined && props.foundryAvailableDatasets.length == 0 &&
              <Alert severity="warning">No datasets found in folder</Alert>
            }
            {props.foundryAvailableDatasets == undefined &&
              <Alert severity="error">Access to folder failed</Alert>
            }
          </DialogContent>
        </Dialog>

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
