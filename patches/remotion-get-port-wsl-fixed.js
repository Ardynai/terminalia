"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPort = exports.getDesiredPort = exports.testPortAvailableOnMultipleHosts = exports.isPortAvailableOnHost = void 0;
const net_1 = __importDefault(require("net"));
const locks_1 = require("./locks");
const isPortAvailableOnHost = ({ portToTry, host }) => {
    return new Promise((resolve) => {
        const srv = net_1.default.createServer();
        srv.once('error', () => resolve('unavailable'));
        srv.listen({ port: portToTry, host: '127.0.0.1' }, () => {
            srv.close(() => resolve('available'));
        });
    });
};
const testPortAvailableOnMultipleHosts = async ({ hosts, port }) => {
    const results = await Promise.all(hosts.map((host) => isPortAvailableOnHost({ portToTry: port, host })));
    return results.some((r) => r === 'available') ? 'available' : 'unavailable';
};
const getDesiredPort = async ({ desiredPort, from, hostsToTry, to, onPortUnavailable }) => {
    const portLocks = (0, locks_1.createLock)({ timeout: 10000 });
    await portLocks.waitForAllToBeDone();
    const lock = portLocks.lock();
    if (typeof desiredPort !== 'undefined') {
        const avail = await testPortAvailableOnMultipleHosts({ hosts: ['127.0.0.1'], port: desiredPort });
        if (avail === 'available') {
            return { port: desiredPort, unlockPort: () => portLocks.unlock(lock), didUsePort: false };
        }
    }
    for (let p = from; p <= to; p++) {
        const avail = await testPortAvailableOnMultipleHosts({ hosts: ['127.0.0.1'], port: p });
        if (avail === 'available') {
            return { port: p, unlockPort: () => portLocks.unlock(lock), didUsePort: false };
        }
    }
    throw new Error('No available ports found');
};
const getPort = async ({ from, to, hostsToTest, onPortUnavailable }) => {
    for (let p = from; p <= to; p++) {
        const avail = await testPortAvailableOnMultipleHosts({ hosts: ['127.0.0.1'], port: p });
        if (avail === 'available') {
            return { port: p, didUsePort: false };
        }
    }
    throw new Error('No available ports found');
};

exports.isPortAvailableOnHost = isPortAvailableOnHost;
exports.testPortAvailableOnMultipleHosts = testPortAvailableOnMultipleHosts;
exports.getDesiredPort = getDesiredPort;
exports.getPort = getPort;
