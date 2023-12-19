import "./App.css";
import Input from "./components/Input";
import Sidebar from "./components/Sidebar";
import Chat, { WaitingStates } from "./components/Chat";
import React, { useState, useEffect  } from "react";
import Config from "./config";
import { useLocalStorage } from "usehooks-ts";

export type MessageDict = {
  text: string;
  role: string;
  type: string;
};

function App() {
  const COMMANDS = ["reset"];

  let [MODELS, setModels] = useState([{displayName: "GPT-3.5", name: "gpt-3.5-turbo"}]);

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
    MODELS[0].name
  );

  let [openAIKey, setOpenAIKey] = useLocalStorage<string>("OpenAIKey", "");
  console.log("test")
  console.error("test2")
  console.info("test3")
  console.debug("test4")
  let [messages, setMessages] = useState<Array<MessageDict>>(
    Array.from([
      {
        text: "Hello! I'm the Pleo GPT Code and Chat assistant. Ask me to do something for you! Pro tip: you can upload a file and I'll be able to use it.",
        role: "generator",
        type: "message",
      },
      {
        text: "If I get stuck just type 'reset' and I'll restart the kernel. 2",
        role: "generator",
        type: "message",
      },
    ])
  );
  let [waitingForSystem, setWaitingForSystem] = useState<WaitingStates>(
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
      .then(() => {})
      .catch((error) => console.error("Error:", error));
  };

  const addMessage = (message: MessageDict) => {
    setMessages((state: any) => {
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
        .then(() => {})
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
     

      

      if (response.status != 200) {
        setWaitingForSystem(WaitingStates.Idle);
        return;
      }
      
      if (!!code) {
        await injectContext(`EXPERT: \n\n ${data.text} \n\n The code you asked for: \n\n ${data.code} \n\n I will now execute it and get back to you with a result and analysis.`)
        submitCode(code);
        setWaitingForSystem(WaitingStates.RunningCode);
        addMessage({ text: data.text, type: "message", role: "generator" });
      } else {
        await injectContext(`EXPERT: \n\n ${data.text} \n\n `)
        setWaitingForSystem(WaitingStates.Idle);
        addMessage({ text: data.text, type: "message", role: "generator" });
      }
    } catch (error) {
      console.error(
        "There has been a problem with your fetch operation:",
        error
      );
    }
  };

  async function getApiData() {
    
    if(document.hidden){
      return;
    }
    console.log("starting the check")
    let response = await fetch(`${Config.API_ADDRESS}/api`);
    //console.log("response:", response)
    let data = await response.json();
    for await (const result of data.results) {
      if (result.value.trim().length === 0) {
        continue;
      }
      if ((result.type === "message" || result.type === "message_raw") && result.value !== 'Kernel is ready.') {
        console.error(`INJECTING DATA: ${result.value}`)
        const chatResponse = await fetch(`${Config.WEB_ADDRESS}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: `Please answer my previous question(s) using the following which is the result the python you wrote. If the code was supposed to generate any visuals, make sure to write a description of them. Take into account what parts of the questions you have already answered. The results are coming in as the server completes the execution. Answer the part of the question that fits the results you are given now.
              [Python code results]:
              ${result.value}`,
            model: selectedModel,
            openAIKey: openAIKey,
          }),
        });

        console.error('Response: ', chatResponse)
        const data = await chatResponse.json();
  
        addMessage({ text: data.text, type: "message", role: "generator" });
        setWaitingForSystem(WaitingStates.Idle);
      } else {
        addMessage({ text: result.value, type: result.type, role: "system" });
        setWaitingForSystem(WaitingStates.Idle);
      }
    }
    /*await data.results.forEach(async function (result: {value: string, type: string}) {
      if (result.value.trim().length == 0) {
        return;
      }

      if ((result.type === "message" || result.type === "message_raw") && result.value !== 'Kernel is ready.') {
        console.error(`INJECTING DATA: ${result.value}`)
        const chatResponse = await fetch(`${Config.WEB_ADDRESS}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: `Please answer my previous question(s) using the following which is the result the python you wrote. If the code was supposed to generate any visuals, make sure to write a description of them. Take into account what parts of the questions you have already answered. The results are coming in as the server completes the execution. Answer the part of the question that fits the results you are given now.
              [Python code results]:
              ${result.value}`,
            model: selectedModel,
            openAIKey: openAIKey,
          }),
        });

        console.error('Response: ', chatResponse)
        const data = await chatResponse.json();
  
        addMessage({ text: data.text, type: "message", role: "generator" });
        setWaitingForSystem(WaitingStates.Idle);
      } else {
        addMessage({ text: result.value, type: result.type, role: "system" });
        setWaitingForSystem(WaitingStates.Idle);
      }
    });*/
  }

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
      .then(() => {})
      .catch((error) => console.error("Error:", error));
  }

  async function injectContext(context: string) {
    await fetch(`${Config.WEB_ADDRESS}/inject-context`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: context,
      }),
    })
      .then(() => {})
      .catch((error) => console.error("Error:", error));
  }

  function startUpload(_: string) {
    setWaitingForSystem(WaitingStates.UploadingFile);
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
