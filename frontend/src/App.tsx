// import React, { useState, useEffect, useRef } from "react";
// import { io, Socket } from "socket.io-client";
// import { Send, Bot, User, Phone, Calendar, AlertCircle } from "lucide-react";
// import "./index.css";

// interface Message {
//   id: string;
//   text: string;
//   sender: "user" | "bot" | "system";
//   timestamp: Date;
//   buttons?: Array<{ title: string; payload: string }>;
// }

// interface ConnectionStatus {
//   connected: boolean;
//   error?: string;
// }

// function App() {
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [inputValue, setInputValue] = useState("");
//   const [socket, setSocket] = useState<Socket | null>(null);
//   const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
//     connected: false,
//   });
//   const [isTyping, setIsTyping] = useState(false);
//   const messagesEndRef = useRef<HTMLDivElement>(null);
//   const sessionId = useRef(generateSessionId());

//   function generateSessionId(): string {
//     return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
//   }

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   useEffect(() => {
//     const newSocket = io(
//       `${window.location.protocol}//${window.location.hostname}:8000`,
//       {
//         path: `/ws/chat/${sessionId.current}`,
//         transports: ["websocket", "polling"],
//       }
//     );

//     newSocket.on("connect", () => {
//       console.log("Connected to server");
//       setConnectionStatus({ connected: true });
//     });

//     newSocket.on("disconnect", () => {
//       console.log("Disconnected from server");
//       setConnectionStatus({ connected: false });
//     });

//     newSocket.on("connect_error", (error) => {
//       console.error("Connection error:", error);
//       setConnectionStatus({ connected: false, error: error.message });
//     });

//     newSocket.on("message", (data) => {
//       try {
//         const messageData = typeof data === "string" ? JSON.parse(data) : data;

//         if (messageData.type === "message") {
//           const newMessage: Message = {
//             id: Date.now().toString(),
//             text: messageData.message,
//             sender: messageData.sender as "user" | "bot" | "system",
//             timestamp: new Date(),
//             buttons: messageData.buttons,
//           };
//           setMessages((prev) => [...prev, newMessage]);

//           if (messageData.sender === "bot") {
//             setIsTyping(false);
//           }
//         } else if (messageData.type === "system") {
//           const systemMessage: Message = {
//             id: Date.now().toString(),
//             text: messageData.message,
//             sender: "system",
//             timestamp: new Date(),
//           };
//           setMessages((prev) => [...prev, systemMessage]);
//         }
//       } catch (error) {
//         console.error("Error parsing message:", error);
//       }
//     });

//     setSocket(newSocket);

//     return () => {
//       newSocket.close();
//     };
//   }, []);

//   const sendMessage = async (message: string) => {
//     if (!message.trim() || !socket) return;

//     const userMessage: Message = {
//       id: Date.now().toString(),
//       text: message,
//       sender: "user",
//       timestamp: new Date(),
//     };

//     setMessages((prev) => [...prev, userMessage]);
//     setInputValue("");
//     setIsTyping(true);

//     // Send message via WebSocket
//     socket.emit("message", {
//       type: "message",
//       message: message,
//       timestamp: new Date().toISOString(),
//     });
//   };

//   const handleButtonClick = (payload: string, title: string) => {
//     if (payload.startsWith("/")) {
//       sendMessage(title); // Send the title as message for intents
//     } else {
//       sendMessage(payload);
//     }
//   };

//   const handleSubmit = (e: React.FormEvent) => {
//     e.preventDefault();
//     sendMessage(inputValue);
//   };

//   const getMessageIcon = (sender: string) => {
//     switch (sender) {
//       case "bot":
//         return <Bot className="w-6 h-6 text-blue-500" />;
//       case "user":
//         return <User className="w-6 h-6 text-green-500" />;
//       case "system":
//         return <AlertCircle className="w-6 h-6 text-yellow-500" />;
//       default:
//         return <Bot className="w-6 h-6 text-gray-500" />;
//     }
//   };

//   const formatTime = (timestamp: Date) => {
//     return timestamp.toLocaleTimeString("en-US", {
//       hour: "2-digit",
//       minute: "2-digit",
//     });
//   };

//   return (
//     <div className="app">
//       <div className="chat-container">
//         <div className="chat-header">
//           <div className="header-content">
//             <Bot className="w-8 h-8 text-white" />
//             <div className="header-text">
//               <h1>Healthcare Assistant</h1>
//               <div className="connection-status">
//                 <div
//                   className={`status-indicator ${
//                     connectionStatus.connected ? "connected" : "disconnected"
//                   }`}
//                 ></div>
//                 <span>
//                   {connectionStatus.connected ? "Connected" : "Disconnected"}
//                 </span>
//               </div>
//             </div>
//           </div>
//         </div>

//         <div className="messages-container">
//           {messages.length === 0 && (
//             <div className="welcome-message">
//               <Bot className="w-12 h-12 text-blue-500 mb-4" />
//               <h2>Welcome to Healthcare Assistant</h2>
//               <p>I can help you with:</p>
//               <ul>
//                 <li>🩺 Symptom assessment and triage</li>
//                 <li>📅 Appointment booking</li>
//                 <li>💊 Health advice and guidance</li>
//                 <li>🚨 Emergency assistance</li>
//               </ul>
//               <p>How can I help you today?</p>
//             </div>
//           )}

//           {messages.map((message) => (
//             <div key={message.id} className={`message ${message.sender}`}>
//               <div className="message-icon">
//                 {getMessageIcon(message.sender)}
//               </div>
import React, { useState, useEffect, useRef } from "react";
import { Bot, User, Phone, Calendar, AlertCircle, Send } from "lucide-react";
import "./index.css";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot" | "system";
  timestamp: Date;
  buttons?: Array<{ title: string; payload: string }>;
}

interface ConnectionStatus {
  connected: boolean;
  error?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    connected: false,
  });
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const sessionId = useRef(
    `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    try {
      // Update this URL to match your backend - adjust hostname/port as needed
      // const wsUrl = `ws://localhost:8000/ws/chat/${sessionId.current}`;

      const getWebSocketUrl = () => {
        if (import.meta.env.VITE_WS_URL) {
          return `${import.meta.env.VITE_WS_URL}/ws/chat/${sessionId.current}`;
        }
        // fallback for host dev
        return `ws://${window.location.hostname}:8000/ws/chat/${sessionId.current}`;
      };

      const wsUrl = getWebSocketUrl();
      console.log(wsUrl, "url");
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setConnectionStatus({ connected: true });
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("Received message:", data);

          if (data.type === "message") {
            const newMessage: Message = {
              id: `${Date.now()}_${Math.random()}`,
              text: data.message,
              sender: data.sender as "user" | "bot" | "system",
              timestamp: new Date(data.timestamp || Date.now()),
              buttons: data.buttons,
            };

            // Only add bot/system messages (user messages are added immediately on send)
            if (data.sender !== "user") {
              setMessages((prev) => [...prev, newMessage]);
              setIsTyping(false);
            }
          } else if (data.type === "system") {
            const systemMessage: Message = {
              id: `${Date.now()}_${Math.random()}`,
              text: data.message,
              sender: "system",
              timestamp: new Date(data.timestamp || Date.now()),
            };
            setMessages((prev) => [...prev, systemMessage]);
          } else if (data.type === "typing") {
            setIsTyping(data.isTyping);
          }
        } catch (error) {
          console.error("Error parsing message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setConnectionStatus({
          connected: false,
          error: "Connection error",
        });
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setConnectionStatus({ connected: false });

        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts.current < 5) {
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttempts.current),
            10000
          );
          console.log(`Reconnecting in ${delay}ms...`);

          reconnectTimeoutRef.current = window.setTimeout(() => {
            reconnectAttempts.current++;
            connectWebSocket();
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
      setConnectionStatus({
        connected: false,
        error: "Failed to connect",
      });
    }
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const sendMessage = (message: string) => {
    if (
      !message.trim() ||
      !wsRef.current ||
      wsRef.current.readyState !== WebSocket.OPEN
    ) {
      console.warn("Cannot send message - WebSocket not ready");
      return;
    }

    // Add user message to UI immediately
    const userMessage: Message = {
      id: `${Date.now()}_${Math.random()}`,
      text: message,
      sender: "user",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Send message via WebSocket
    const messageData = {
      type: "message",
      message: message,
      timestamp: new Date().toISOString(),
    };

    console.log("Sending message:", messageData);
    wsRef.current.send(JSON.stringify(messageData));
  };

  const handleButtonClick = (payload: string, title: string) => {
    // Send the payload or title depending on format
    sendMessage(payload.startsWith("/") ? title : payload);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const getMessageIcon = (sender: string) => {
    switch (sender) {
      case "bot":
        return <Bot className="w-6 h-6 text-blue-500" />;
      case "user":
        return <User className="w-6 h-6 text-green-500" />;
      case "system":
        return <AlertCircle className="w-6 h-6 text-yellow-500" />;
      default:
        return <Bot className="w-6 h-6 text-gray-500" />;
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-content">
            <Bot className="w-8 h-8 text-white" />
            <div className="header-text">
              <h1>Healthcare Assistant</h1>
              <div className="connection-status">
                <div
                  className={`status-indicator ${
                    connectionStatus.connected ? "connected" : ""
                  }`}
                ></div>
                <span>
                  {connectionStatus.connected ? "Connected" : "Disconnected"}
                </span>
                {connectionStatus.error && (
                  <span style={{ fontSize: "12px" }}>
                    ({connectionStatus.error})
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <Bot
                className="w-12 h-12 text-blue-500 mb-4"
                style={{ margin: "0 auto 16px" }}
              />
              <h2>Welcome to Healthcare Assistant</h2>
              <p>I can help you with:</p>
              <ul>
                <li>🩺 Symptom assessment and triage</li>
                <li>📅 Appointment booking</li>
                <li>💊 Health advice and guidance</li>
                <li>🚨 Emergency assistance</li>
              </ul>
              <p>How can I help you today?</p>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              <div className="message-icon">{getMessageIcon(msg.sender)}</div>

              <div className="message-content">
                <div className="message-text">{msg.text}</div>
                <div className="message-time">{formatTime(msg.timestamp)}</div>

                {msg.buttons && msg.buttons.length > 0 && (
                  <div className="message-buttons">
                    {msg.buttons.map((btn, i) => (
                      <button
                        key={i}
                        onClick={() =>
                          handleButtonClick(btn.payload, btn.title)
                        }
                        className="message-button"
                      >
                        {btn.title.includes("Symptom") && (
                          <Phone
                            style={{
                              width: "16px",
                              height: "16px",
                              marginRight: "8px",
                            }}
                          />
                        )}
                        {btn.title.includes("Appointment") && (
                          <Calendar
                            style={{
                              width: "16px",
                              height: "16px",
                              marginRight: "8px",
                            }}
                          />
                        )}
                        {btn.title}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="message bot typing">
              <div className="message-icon">
                <Bot className="w-6 h-6 text-blue-500" />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              connectionStatus.connected
                ? "Type your message..."
                : "Connecting..."
            }
            disabled={!connectionStatus.connected}
            className="message-input"
          />
          <button
            type="submit"
            disabled={!connectionStatus.connected || !inputValue.trim()}
            className="send-button"
          >
            <Send style={{ width: "20px", height: "20px" }} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
