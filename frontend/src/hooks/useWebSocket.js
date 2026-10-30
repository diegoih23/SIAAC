import { useEffect, useRef, useState } from "react";

const WS_URL = import.meta.env.VITE_WS_URL || `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`;

/** Hook genérico con reconexión automática para los canales de Channels. */
export function useWebSocket(path, { enabled = true, onMessage } = {}) {
  const socketRef = useRef(null);
  const retryRef = useRef(0);
  const [status, setStatus] = useState("disconnected");
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    if (!enabled || !path) return undefined;
    let closedByUser = false;

    const connect = () => {
      setStatus("connecting");
      const token = localStorage.getItem("siaac_access");
      const separator = path.includes("?") ? "&" : "?";
      const url = token ? `${WS_URL}${path}${separator}token=${token}` : `${WS_URL}${path}`;
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        retryRef.current = 0;
        setStatus("connected");
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch {
          // Ignora mensajes que no sean JSON.
        }
      };

      socket.onclose = () => {
        setStatus("disconnected");
        if (!closedByUser && retryRef.current < 8) {
          retryRef.current += 1;
          setTimeout(connect, Math.min(1000 * retryRef.current, 10000));
        }
      };

      socket.onerror = () => socket.close();
    };

    connect();
    return () => {
      closedByUser = true;
      socketRef.current?.close();
    };
  }, [path, enabled, onMessage]);

  const send = (data) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(typeof data === "string" ? data : JSON.stringify(data));
    }
  };

  return { status, lastMessage, send };
}
