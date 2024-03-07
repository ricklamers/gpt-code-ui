import "./App.css";
import Input from "./components/Input";
import Sidebar from "./components/Sidebar";
import Chat, { WaitingStates } from "./components/Chat";
import React, { useState, useEffect } from "react";
import Config from "./config";
import { useLocalStorage } from "usehooks-ts";

export type MessageDict = {
  text: string;
  role: string;
  type: string;
};

function App() {
  const COMMANDS = ["reset"];

  const [MODELS, setModels] = useState([{ displayName: "GPT-3.5", name: "gpt-3.5-turbo" }]);

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
    MODELS[0].name
  );

  const [openAIKey, setOpenAIKey] = useLocalStorage<string>("OpenAIKey", "");

  const [messages, setMessages] = useState<Array<MessageDict>>(
    Array.from([
      {
        text: "Hello! I'm a GPT Code assistant. Ask me to do something for you! Pro tip: you can upload a file and I'll be able to use it.",
        role: "generator",
        type: "message",
      },
      {
        text: "If I get stuck just type 'reset' and I'll restart the kernel.",
        role: "generator",
        type: "message",
      },
    ])
  );
  const [waitingForSystem, setWaitingForSystem] = useState<WaitingStates>(
    WaitingStates.Idle
  );
  const chatScrollRef = React.useRef<HTMLDivElement>(null);

  const submitCode = async (code: string) => {
    fetch(`${Config.API_ADDRESS}/api`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ command: code }),
    })
      .then(() => {
        // do nothing
      })
      .catch((error) => console.error("Error:", error));
  };

  const prependHistory = (history: string) => {
    setMessages((state) => {
      return [
        { text: history, type: "message", role: "system" },
        ...state,
      ];
    });
  };

  const loadHistory = () => {
    fetch(`${Config.API_ADDRESS}/history`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        prependHistory(data.history);
      })
      .catch((error) => console.error("Error:", error));
  }

  const addMessage = (message: MessageDict) => {
    setMessages((state) => {
      return [...state, message];
    });
  };

  const handleCommand = (command: string) => {
    if (command == "reset") {
      addMessage({ text: "Restarting the kernel.", type: "message", role: "system" });

      fetch(`${Config.API_ADDRESS}/restart`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      })
        .then(() => {
          // do nothing
        })
        .catch((error) => console.error("Error:", error));
    }
  };

  const sendMessage = async (userInput: string) => {
    try {
      if (COMMANDS.includes(userInput)) {
        handleCommand(userInput);
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
          openAIKey: openAIKey,
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

    // Inform prompt server
    fetch(`${Config.WEB_ADDRESS}/inject-context`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: message,
      }),
    })
      .then(() => {
        // do nothing
      })
      .catch((error) => console.error("Error:", error));
  }

  function startUpload(_: string) {
    setWaitingForSystem(WaitingStates.UploadingFile);
  }

  React.useEffect(() => {
    async function getApiData() {
      if (document.hidden) {
        return;
      }

      const response = await fetch(`${Config.API_ADDRESS}/api`);
      const data = await response.json();
      data.results.forEach(function (result: { value: string, type: string }) {
        if (result.value.trim().length == 0) {
          return;
        }

        addMessage({ text: result.value, type: result.type, role: "system" });
        setWaitingForSystem(WaitingStates.Idle);
      });
    }

    const interval = setInterval(getApiData, 1000);
    return () => clearInterval(interval);
  }, [addMessage, setWaitingForSystem]);

  React.useEffect(() => {
    // Scroll down container by setting scrollTop to the height of the container
    chatScrollRef.current!.scrollTop = chatScrollRef.current!.scrollHeight;
  }, [chatScrollRef, messages]);


  // Capture <a> clicks for download links
  React.useEffect(() => {
    loadHistory();

    const clickHandler = (event: any) => {
      const element = event.target;

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
        <Sidebar
          models={MODELS}
          selectedModel={selectedModel}
          onSelectModel={(val: string) => {
            setSelectedModel(val);
          }}
          openAIKey={openAIKey}
          setOpenAIKey={(val: string) => {
            setOpenAIKey(val);
          }}
        />
        <div className="main">
          <Chat
            chatScrollRef={chatScrollRef}
            waitingForSystem={waitingForSystem}
            messages={messages}
          />
          <Input
            onSendMessage={sendMessage}
            onCompletedUpload={completeUpload}
            onStartUpload={startUpload}
          />
        </div>
      </div>
    </>
  );
}

export default App;
