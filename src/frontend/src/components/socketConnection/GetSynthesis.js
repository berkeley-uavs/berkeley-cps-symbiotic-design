import React, { useCallback, useEffect } from "react";
import { useSocket } from "../../socket/SocketProvider";

function SocketGetSynthesis(props) {
  const socket = useSocket();

  const setGraph = useCallback(
    (graph) => {
      console.log(graph);
      if (graph) {
        props.setGraph(graph);
      } else {
        props.setGraph(null);
      }
      socket.off("design-created");
    },
    [props, socket]
  ); // eslint-disable-next-line

  useEffect(() => {
    if (socket == null) return;

    if (props.trigger && props.name !== "") {
      if (props.strategy_random) {
        socket.emit("create-design", {
          strategy: "strategy_random",
          name: props.name,
        });
      } else if (props.strategy_another) {
        socket.emit("create-design", {
          strategy: "strategy_another",
          name: props.name,
        });
      }
      socket.on("design-created", setGraph);

      props.setTrigger(false);

      return () => socket.off("graph-generated");
    }
  }, [socket, props, setGraph]);

  return <></>;
}

export default SocketGetSynthesis;
