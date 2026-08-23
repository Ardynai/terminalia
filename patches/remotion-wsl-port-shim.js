// WSL mirrored-networking fix for @remotion/renderer get-port.js:
// connect-based port probes hang on free ports under mirrored mode, so every
// port looks "unavailable". This preload rewrites localhost connects to fail
// fast with ECONNREFUSED, which remotion treats as "port is free".
//
// Usage: NODE_OPTIONS="--require /path/to/remotion-wsl-port-shim.js" npx remotion render ...
const net = require("net");
const origConnect = net.Socket.prototype.connect;
net.Socket.prototype.connect = function (...args) {
  const target = args[0];
  const host = typeof target === "object" ? target.host : args[1];
  if (host === "localhost" || host === "127.0.0.1") {
    process.nextTick(() =>
      this.emit("error", Object.assign(
        new Error("ECONNREFUSED (terminalia mirrored-net shim)"),
        { code: "ECONNREFUSED" })));
    return this;
  }
  return origConnect.apply(this, args);
};
