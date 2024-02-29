import "./App.css";
import Input from "./components/Input";
import Logo from "./components/Logo"
import Documentation from "./components/Documentation";
import Kernel from "./components/Kernel";
import Settings from "./components/Settings";
import Chat, { WaitingStates } from "./components/Chat";
import React, { useState, useEffect } from "react";
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Config from "./config";
import { useLocalStorage } from "usehooks-ts";
import { v4 as uuidv4 } from 'uuid';

export type MessageDict = {
  text: string;
  role: string;
  type: string;
};

let tabID = 'undefined';

function App() {
  // map from user command to kernel api endpoint, info message, etc.
  const COMMANDS = {
    "reset": {
      endpoint: `${Config.API_ADDRESS}/restart`,
      status: WaitingStates.WaitingForKernel,
      message: "Restarting the kernel.",
      onSuccess: () => {}
    },
    "clear": {
      endpoint: `${Config.WEB_ADDRESS}/clear_history`,
      status: WaitingStates.Idle,
      message: "Clearing chat history.",
      onSuccess: () => { setMessages(DEFAULT_MESSAGES); }
    },
    "stop": {
      endpoint: `${Config.API_ADDRESS}/interrupt`,
      status: WaitingStates.WaitingForKernel,
      message: "Interrupting code execution.",
      onSuccess: () => {}
    },
  };

  let [MODELS, setModels] = useState<{displayName: string, name: string}[]>([]);

  useEffect(() => {
    const getModels = async () => {
      try {
        const response = await fetch(`${Config.WEB_ADDRESS}/models`);
        const json = await response.json();
        setModels(json);
      } catch (e) {
        console.error(e);
      };
    };

    getModels();
 }, []);

  let [selectedModel, setSelectedModel] = useLocalStorage<string>(
    "model",
    "gpt-3.5-turbo"
  );

  let [toggledOptions, setToggledOptions] = React.useState<string[]>(['svg', ]);

  let [foundryFolder, setFoundryFolder] = useLocalStorage<string | undefined>('foundryFolder', undefined)
  let [foundryAvailableDatasets, setFoundryAvailableDatasets] = useState<{ name: string; dataset_rid: string; }[] | undefined>(undefined)

  const selectFoundryFolder = async (folder: string | undefined) => {
    setFoundryFolder(folder);
    try {
      if (folder != undefined) {
        const response = await fetch(`${Config.WEB_ADDRESS}/foundry_files?` + new URLSearchParams({folder: folder}));
        if (response.ok) {
          const json = await response.json();
          setFoundryAvailableDatasets(json.datasets);
        } else {
          setFoundryAvailableDatasets(undefined);
        }

      } else {
        const response = await fetch(`${Config.WEB_ADDRESS}/foundry_files`);
        const json = await response.json();
        setFoundryFolder(json.folder);
        setFoundryAvailableDatasets(json.datasets);
      }
    } catch (e) {
      console.error(e);
      setFoundryAvailableDatasets(undefined);
    };
  }

  useEffect(() => {
    selectFoundryFolder(foundryFolder);
  }, []);

  const DEFAULT_MESSAGES = Array.from([
    {
      text: `Hello! I am a GPT Code assistant. Ask me to do something for you!
Pro tip: you can upload a file and I'll be able to use it.`,
      role: "generator",
      type: "message",
    },
    {
      text: `If I get stuck just type <kbd>reset<kbd>⮐</kbd></kbd> and I'll restart the kernel.
For interrupting a running program, please type <kbd>stop<kbd>⮐</kbd></kbd>.
In case you want to clear the conversation history, just type <kbd>clear<kbd>⮐</kbd></kbd>.
Use <kbd><kbd>Alt</kbd>+<kbd>&uarr;</kbd></kbd> and <kbd><kbd>Alt</kbd>+<kbd>&darr;</kbd></kbd> to recall previous prompts.`,
      role: "generator",
      type: "message",
    },
  ]);

  useEffect(() => {
    tabID = uuidv4();
  }, []);

  let [otherTabDetected, setOtherTabDetected] = useState(false);

  const channel = new BroadcastChannel('cross-tab-communication');
  channel.addEventListener('message', (msg) => {
    if (msg.data.type == 'new tab') {
      setOtherTabDetected(msg.data.id != tabID);
    }
  });

  const continueSession = () => {
    channel.postMessage({
      type: 'new tab',
      id: tabID,
    });
  };

  useEffect(() => {
    continueSession();
  }, []);



  let [messages, setMessages] = useState<MessageDict[]>(DEFAULT_MESSAGES);
  let [waitingForSystem, setWaitingForSystem] = useState<WaitingStates>(WaitingStates.Idle);
  const chatScrollRef = React.useRef<HTMLDivElement>(null);

  const submitCode = async (code: string) => {
    fetch(`${Config.API_ADDRESS}/api`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ command: code, options: toggledOptions }),
    })
      .then(() => {})
      .catch((error) => console.error("Error:", error));
  };

  const addMessage = (message: MessageDict) => {
    setMessages((state: MessageDict[]) => {
      return [...state, message];
    });
  };

  const handleCommand = ({endpoint, message,  status, onSuccess}: {endpoint:string, message: string, status: WaitingStates, onSuccess: () => void}) => {
    addMessage({ text: message, type: "message", role: "system" });
    setWaitingForSystem(status);
    fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    })
      .then(onSuccess)
      .catch((error) => console.error("Error:", error));
  };

  const sendMessage = async (userInput: string) => {
    try {
      if(userInput.toLowerCase() in COMMANDS) {
        handleCommand(COMMANDS[userInput.toLowerCase() as keyof typeof COMMANDS])
        return;
      }

      if (userInput.length == 0) {
        return;
      }

      addMessage({ text: userInput, type: "message", role: "user" });
      setWaitingForSystem(WaitingStates.GeneratingCode);

      const response = await fetch(`${Config.WEB_ADDRESS}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: userInput,
          model: selectedModel,
        }),
      });

      const data = await response.json();
      const code = data.code;

      addMessage({ text: data.text, type: "message", role: "generator" });

      if (response.status != 200) {
        setWaitingForSystem(WaitingStates.Idle);
        return;
      }

      if (!!code) {
        submitCode(code);
        setWaitingForSystem(WaitingStates.RunningCode);
      } else {
        setWaitingForSystem(WaitingStates.Idle);
      }
    } catch (error) {
      console.error(
        "There has been a problem with your fetch operation:",
        error
      );
    }
  };

  async function getApiData() {
    if (document.hidden || otherTabDetected){
      return;
    }

    try {
      let response = await fetch(`${Config.API_ADDRESS}/api`, {redirect: 'manual'});
      if (response.type === 'opaqueredirect') {
        // redirect occurs in the AppService when a new login is required. We could reload automatically,
        // but that would lead to the user loosing their previous results.
        setWaitingForSystem(WaitingStates.SessionTimeout);
      } else {
        let data = await response.json();

        if (data.status === "starting") {
          setWaitingForSystem(WaitingStates.WaitingForKernel);
        } else if (data.status === "ready") {
          setWaitingForSystem(WaitingStates.Idle);
        } else if (data.status === "idle") {
          setWaitingForSystem(WaitingStates.Idle);
        } else if (data.status === "generating") {
          setWaitingForSystem(WaitingStates.GeneratingCode);
        } else if (data.status === "busy") {
          setWaitingForSystem(WaitingStates.RunningCode);
        } else {
          setWaitingForSystem(WaitingStates.WaitingForKernel);
        }

        data.results.forEach(function (result: {value: string, type: string}) {
          if (result.value.trim().length == 0) {
            return;
          }

          addMessage({ text: result.value, type: result.type, role: "system" });
        });
      }
    } catch (error) {
      if (error instanceof(TypeError)) {
        if (waitingForSystem != WaitingStates.WaitingForKernel) {
          setWaitingForSystem(WaitingStates.WaitingForKernel);
        }
      } else {
        console.error('Error while fetching from api: ' + error);
      }
    }
  }

  function completeUpload(message: string) {
    addMessage({ text: message, type: "message", role: "upload" });
    setWaitingForSystem(WaitingStates.Idle);
  }

  function startUpload(_: string) {
    setWaitingForSystem(WaitingStates.UploadingFile);
  }

  async function selectFoundryDataset(dataset_rid: string) {
    if (dataset_rid != '') {
      try {
        setWaitingForSystem(WaitingStates.UploadingFile);
        const response = await fetch(`${Config.WEB_ADDRESS}/foundry_files`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ "dataset_rid": dataset_rid }),
        });
        if (response.ok) {
          const json = await response.json();
          json.map((file: {message: string, filename: string}) => {
              addMessage({ text: file.message, type: "message", role: "upload" });
          });
        } else {
          const msg = await response.text();
          addMessage({ text: `Downloading dataset <a href="https://palantir.mcloud.merckgroup.com/workspace/hubble/exploration?objectId=${dataset_rid}" target="_blank">${dataset_rid}</a> failed with status code ${response.status}: ${msg}.
Likely, you only have Discoverer role but need at least Reader role in the <a href="https://palantir.mcloud.merckgroup.com/workspace/compass/view/${foundryFolder}" target="_blank">specified folder</a>.`, type: "message", role: "upload" });
          console.log(response);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setWaitingForSystem(WaitingStates.Idle);
      };
    }
  }

  React.useEffect(() => {
    const interval = setInterval(getApiData, 1000);
    return () => clearInterval(interval);
  }, [getApiData]);

  React.useEffect(() => {
    // Scroll down container by setting scrollTop to the height of the container
    chatScrollRef.current!.scrollTop = chatScrollRef.current!.scrollHeight;
  }, [chatScrollRef, messages]);


  // Capture <a> clicks for download links
  React.useEffect(() => {
    const clickHandler = (event: any) => {
      let element = event.target;

      // If an <a> element was found, prevent default action and do something else
      if (element != null && element.tagName === 'A') {
        // Check if href starts with /download

        if (element.getAttribute("href").startsWith(`/download`)) {
          event.preventDefault();

          // Make request to ${Config.WEB_ADDRESS}/download instead
          // make it by opening a new tab
          window.open(`${Config.WEB_ADDRESS}${element.getAttribute("href")}`);
        }
      }
    };

    // Add the click event listener to the document
    document.addEventListener('click', clickHandler);

    // Cleanup function to remove the event listener when the component unmounts
    return () => {
      document.removeEventListener('click', clickHandler);
    };
  }, []);

  return (
    <>
      <div className="app">
        <Dialog
          open={otherTabDetected}
          aria-labelledby="additional-tab-dialog-title"
          aria-describedby="additional-tab-dialog-description"
        >
          <DialogTitle id="additional-tab-dialog-title">
            {"Another Browser Tab Detected"}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="additional-tab-dialog-description">
              CodeImpact does not support multiple sessions in different
              browser tabs. The session in this tab has been suspended.
              You can either close this browser tab/window or press the button
              below to continue your work here and suspend sessions
              in all other open tabs.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={continueSession} autoFocus>
              Continue Here
            </Button>
          </DialogActions>
        </Dialog>

        <Stack
          direction="column"
          justifyContent="space-between"
          alignItems="stretch"
          sx={{ padding: "0.75rem" }}
        >
            <Logo />
            <Documentation />
            <Kernel
              state={waitingForSystem}
              onClearChat={() => { handleCommand(COMMANDS["clear"]); }}
              onInterruptKernel={() => { handleCommand(COMMANDS["stop"]); }}
              onResetKernel={() => { handleCommand(COMMANDS["reset"]); }}
            />
            <Settings
              models={MODELS}
              selectedModel={selectedModel}
              onSelectModel={(val: string) => {
                setSelectedModel(val);
              }}
              toggledOptions={toggledOptions}
              onToggledOptions={(val: string[]) => {
                setToggledOptions(val);
              }}
            />
        </Stack>
        <div className="main">
          <Chat
            chatScrollRef={chatScrollRef}
            waitingForSystem={waitingForSystem}
            messages={messages}
          />
          <Input
            Messages={messages}
            onSendMessage={sendMessage}
            onCompletedUpload={completeUpload}
            onStartUpload={startUpload}
            onSelectFoundryFolder={selectFoundryFolder}
            foundryFolder={foundryFolder}
            foundryAvailableDatasets={foundryAvailableDatasets}
            onSelectFoundryDataset={selectFoundryDataset}
          />
        </div>
      </div>
    </>
  );
}

export default App;
