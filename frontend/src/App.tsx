import "./App.css";
import Input from "./components/Input";
import Logo from "./components/Logo"
import Documentation from "./components/Documentation";
import Kernel from "./components/Kernel";
import Settings from "./components/Settings";
import Chat, { WaitingStates } from "./components/Chat";
import React, { useState, useEffect, useCallback } from "react";
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Config from "./config";
import useLocalStorage from "use-local-storage";
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

  const [showCode, setShowCode] = useLocalStorage<boolean>("showCode", false);
  const [autoFix, setAutoFix] = useLocalStorage<number>("autoFix", 0);
  const [autoFixCountdown, setAutoFixCountdown] = useState(autoFix);
  const [MODELS, setModels] = useState<{displayName: string, name: string}[]>([]);

  useEffect(() => {
    const getModels = async () => {
      try {
        const response = await fetch(`${Config.WEB_ADDRESS}/models`);
        const json = await response.json();
        setModels(json);
      } catch (e) {
        console.error(e);
      }
    };

    getModels();
 }, []);

  const [selectedModel, setSelectedModel] = useLocalStorage<string>(
    "model",
    "gpt-3.5-turbo"
  );

  const [toggledOptions, setToggledOptions] = React.useState<string[]>(['svg', ]);

  const [foundryFolder, setFoundryFolder] = useLocalStorage<string | undefined>('foundryFolder', undefined)
  const [foundryAvailableDatasets, setFoundryAvailableDatasets] = useState<{ name: string; dataset_rid: string; }[] | undefined>(undefined)

  const getAvailableFoundryDatasets = async (folder: string | undefined) => {
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
        setFoundryAvailableDatasets(undefined);
      }
    } catch (e) {
      console.error(e);
      setFoundryAvailableDatasets(undefined);
    }
  };

  useEffect(() => {
    getAvailableFoundryDatasets(foundryFolder);
  }, [foundryFolder]);

  const DEFAULT_MESSAGES = Array.from([
    {
      text: `Hello! I am a GPT Code assistant. Ask me to do something for you!
Pro tip: you can upload a file and I'll be able to use it.`,
      role: "documentation",
      type: "message",
    },
    {
      text: `If I get stuck just type <kbd>reset<kbd>⮐</kbd></kbd> and I'll restart the kernel.
For interrupting a running program, please type <kbd>stop<kbd>⮐</kbd></kbd>.
In case you want to clear the conversation history, just type <kbd>clear<kbd>⮐</kbd></kbd>.
Use <kbd><kbd>Alt</kbd>+<kbd>&uarr;</kbd></kbd> and <kbd><kbd>Alt</kbd>+<kbd>&darr;</kbd></kbd> to recall previous prompts.`,
      role: "documentation",
      type: "message",
    },
  ]);

  useEffect(() => {
    tabID = uuidv4();
  }, []);

  const [otherTabDetected, setOtherTabDetected] = useState(false);

  const continueSession = useCallback(() => {
    const channel = new BroadcastChannel('cross-tab-communication');
    channel.addEventListener('message', (msg) => {
      if (msg.data.type == 'new tab') {
        setOtherTabDetected(msg.data.id != tabID);
      }
    });

    channel.postMessage({
      type: 'new tab',
      id: tabID,
    });
  }, []);

  useEffect(() => {
    continueSession();
  }, [continueSession]);

  const [messages, setMessages] = useState<MessageDict[]>(DEFAULT_MESSAGES);
  const [waitingForSystem, setWaitingForSystem] = useState<WaitingStates>(WaitingStates.Idle);
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

  const handleUserInput = async (userInput: string) => {
    if(userInput.toLowerCase() in COMMANDS) {
      handleCommand(COMMANDS[userInput.toLowerCase() as keyof typeof COMMANDS])
    } else if (userInput.length > 0) {
      setAutoFixCountdown(autoFix);
      sendMessage(userInput, 'user');
      setWaitingForSystem(WaitingStates.GeneratingCode);
    }
  }

  const sendMessage = async (userInput: string, role: string) => {
      addMessage({ text: userInput, type: 'message', role: role });

      try {
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

      if (code) {
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

  function completeUpload(message: string) {
    addMessage({ text: message, type: "message", role: "upload" });
    setWaitingForSystem(WaitingStates.Idle);
  }

  function startUpload() {
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
          addMessage({ text: `Downloading dataset <a href="https://YOUR_FOUNDRY_SERVER/workspace/hubble/exploration?objectId=${dataset_rid}" target="_blank">${dataset_rid}</a> failed with status code ${response.status}: ${msg}.
Likely, you only have Discoverer role but need at least Reader role in the <a href="https://YOUR_FOUNDRY_SERVER/workspace/compass/view/${foundryFolder}" target="_blank">specified folder</a>.`, type: "message", role: "upload" });
          console.log(response);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setWaitingForSystem(WaitingStates.Idle);
      }
    }
  }

  React.useEffect(() => {

    async function getApiData() {
      if (document.hidden || otherTabDetected){
        return;
      }

      try {
        const response = await fetch(`${Config.API_ADDRESS}/api`, {redirect: 'manual'});
        if (response.type === 'opaqueredirect') {
          // redirect occurs in the AppService when a new login is required. We could reload automatically,
          // but that would lead to the user loosing their previous results.
          setWaitingForSystem(WaitingStates.SessionTimeout);
        } else {
          const data = await response.json();

          switch (data.status) {
            case "starting":
              setWaitingForSystem(WaitingStates.WaitingForKernel);
              break;
            case "ready":
            case "idle":
              setWaitingForSystem(WaitingStates.Idle);
              break;
            case "generating":
              setWaitingForSystem(WaitingStates.GeneratingCode);
              break;
            case "busy":
              setWaitingForSystem(WaitingStates.RunningCode);
              break;
            default:
              setWaitingForSystem(WaitingStates.WaitingForKernel);
          }

          data.results.forEach(function (result: {value: string, type: string}) {
            if (result.value.trim().length == 0) {
              return;
            }

            addMessage({ text: result.value, type: result.type, role: "system" });
          });

          if ((data.results.at(-1)?.type == 'message_error') && (autoFix > 0)) {
            // we got a runtime error. Mark all previous results as potentially incomplete
            setMessages((state: MessageDict[]) =>
             {
              for (let step = state.length - 1; step > 0; step--) {
                if (state[step].role != 'system') {
                  // this is likely the latest user prompt or generator output - do not go further back
                  break;
                } else {
                  state[step].role = 'system_hide';
                }
              }
              return state;
            });

            if (autoFixCountdown > 0) {
              setAutoFixCountdown(autoFixCountdown - 1);
              setWaitingForSystem(WaitingStates.FixingCode);
              await sendMessage('Please fix the error.', 'generator');
            } else {
              addMessage({ text: `Automatic fixing of execution errors failed after ${autoFix} attempts. Please check your input.`, type: 'message', role: 'system' })
            }
          }
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

    const interval = setInterval(getApiData, 1000);
    return () => clearInterval(interval);
  }, [autoFix, autoFixCountdown, otherTabDetected]);

  React.useEffect(() => {
    // Scroll down container by setting scrollTop to the height of the container
    chatScrollRef.current!.scrollTop = chatScrollRef.current!.scrollHeight;
  }, [chatScrollRef, messages]);


  // Capture <a> clicks for download links
  React.useEffect(() => {
    const clickHandler = (event: MouseEvent) => {
      const element = event.target as HTMLElement;

      // If an <a> element was found, prevent default action and do something else
      if (element != null && element.tagName === 'A') {
        // Check if href starts with /download

        if (element.getAttribute("href")?.startsWith(`/download`)) {
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
              This tool does not support multiple sessions in different
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
          className="sidebar"
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
              onSelectModel={setSelectedModel}
              toggledOptions={toggledOptions}
              onToggledOptions={setToggledOptions}
              showCode={showCode}
              onShowCode={setShowCode}
              autoFix={autoFix}
              onAutoFix={setAutoFix}
            />
        </Stack>
        <div className="main">
          <Chat
            chatScrollRef={chatScrollRef}
            waitingForSystem={waitingForSystem}
            messages={messages}
            showCode={showCode}
          />
          <Input
            Messages={messages}
            onSendMessage={handleUserInput}
            onCompletedUpload={completeUpload}
            onStartUpload={startUpload}
            onSelectFoundryFolder={setFoundryFolder}
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
