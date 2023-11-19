/**
 * Skipped minification because the original files appears to be already minified.
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
!function(t,e){"object"==typeof exports&&"object"==typeof module?module.exports=e():"function"==typeof define&&define.amd?define([],e):"object"==typeof exports?exports.VueNativeSock=e():t.VueNativeSock=e()}(this,function(){return function(t){function e(o){if(n[o])return n[o].exports;var r=n[o]={i:o,l:!1,exports:{}};return t[o].call(r.exports,r,r.exports,e),r.l=!0,r.exports}var n={};return e.m=t,e.c=n,e.d=function(t,n,o){e.o(t,n)||Object.defineProperty(t,n,{configurable:!1,enumerable:!0,get:o})},e.n=function(t){var n=t&&t.__esModule?function(){return t.default}:function(){return t};return e.d(n,"a",n),n},e.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},e.p="",e(e.s=1)}([function(t,e,n){"use strict";function o(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(e,"__esModule",{value:!0});var r=function(){function t(t,e){for(var n=0;n<e.length;n++){var o=e[n];o.enumerable=o.enumerable||!1,o.configurable=!0,"value"in o&&(o.writable=!0),Object.defineProperty(t,o.key,o)}}return function(e,n,o){return n&&t(e.prototype,n),o&&t(e,o),e}}(),i=function(){function t(){o(this,t),this.listeners=new Map}return r(t,[{key:"addListener",value:function(t,e,n){return"function"==typeof e&&(this.listeners.has(t)||this.listeners.set(t,[]),this.listeners.get(t).push({callback:e,vm:n}),!0)}},{key:"removeListener",value:function(t,e,n){var o=this.listeners.get(t),r=void 0;return!!(o&&o.length&&(r=o.reduce(function(t,o,r){return"function"==typeof o.callback&&o.callback===e&&o.vm===n&&(t=r),t},-1))>-1)&&(o.splice(r,1),this.listeners.set(t,o),!0)}},{key:"emit",value:function(t){for(var e=arguments.length,n=Array(e>1?e-1:0),o=1;o<e;o++)n[o-1]=arguments[o];var r=this.listeners.get(t);return!(!r||!r.length)&&(r.forEach(function(t){var e;(e=t.callback).call.apply(e,[t.vm].concat(n))}),!0)}}]),t}();e.default=new i},function(t,e,n){t.exports=n(2)},function(t,e,n){"use strict";function o(t){return t&&t.__esModule?t:{default:t}}Object.defineProperty(e,"__esModule",{value:!0});var r=n(3),i=o(r),s=n(0),c=o(s);e.default={install:function(t,e){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};if(!e&&!n.connectManually)throw new Error("[vue-native-socket] cannot locate connection");var o=null;n.$setInstance=function(e){t.prototype.$socket=e},n.connectManually?(t.prototype.$connect=function(){var r=arguments.length>0&&void 0!==arguments[0]?arguments[0]:e,s=arguments.length>1&&void 0!==arguments[1]?arguments[1]:n;s.$setInstance=n.$setInstance,o=new i.default(r,s),t.prototype.$socket=o.WebSocket},t.prototype.$disconnect=function(){o&&o.reconnection&&(o.reconnection=!1),t.prototype.$socket&&(t.prototype.$socket.close(),delete t.prototype.$socket)}):(o=new i.default(e,n),t.prototype.$socket=o.WebSocket);var r="undefined"!=typeof Proxy&&"function"==typeof Proxy&&/native code/.test(Proxy.toString());t.mixin({created:function(){var t=this,e=this,n=this.$options.sockets;r?(this.$options.sockets=new Proxy({},{set:function(t,n,o){return c.default.addListener(n,o,e),t[n]=o,!0},deleteProperty:function(t,n){return c.default.removeListener(n,e.$options.sockets[n],e),delete t.key,!0}}),n&&Object.keys(n).forEach(function(e){t.$options.sockets[e]=n[e]})):(Object.seal(this.$options.sockets),n&&Object.keys(n).forEach(function(t){c.default.addListener(t,n[t],e)}))},beforeDestroy:function(){var t=this;if(r){var e=this.$options.sockets;e&&Object.keys(e).forEach(function(e){delete t.$options.sockets[e]})}}})}}},function(t,e,n){"use strict";function o(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}Object.defineProperty(e,"__esModule",{value:!0});var r=function(){function t(t,e){for(var n=0;n<e.length;n++){var o=e[n];o.enumerable=o.enumerable||!1,o.configurable=!0,"value"in o&&(o.writable=!0),Object.defineProperty(t,o.key,o)}}return function(e,n,o){return n&&t(e.prototype,n),o&&t(e,o),e}}(),i=n(0),s=function(t){return t&&t.__esModule?t:{default:t}}(i),c=function(){function t(e){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};if(o(this,t),this.format=n.format&&n.format.toLowerCase(),e.startsWith("//")){e=("https:"===window.location.protocol?"wss":"ws")+":"+e}this.connectionUrl=e,this.opts=n,this.reconnection=this.opts.reconnection||!1,this.reconnectionAttempts=this.opts.reconnectionAttempts||1/0,this.reconnectionDelay=this.opts.reconnectionDelay||1e3,this.reconnectTimeoutId=0,this.reconnectionCount=0,this.passToStoreHandler=this.opts.passToStoreHandler||!1,this.connect(e,n),n.store&&(this.store=n.store),n.mutations&&(this.mutations=n.mutations),this.onEvent()}return r(t,[{key:"connect",value:function(t){var e=this,n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},o=n.protocol||"";return this.WebSocket=n.WebSocket||(""===o?new WebSocket(t):new WebSocket(t,o)),"json"===this.format&&("sendObj"in this.WebSocket||(this.WebSocket.sendObj=function(t){return e.WebSocket.send(JSON.stringify(t))})),this.WebSocket}},{key:"reconnect",value:function(){var t=this;this.reconnectionCount<=this.reconnectionAttempts?(this.reconnectionCount++,clearTimeout(this.reconnectTimeoutId),this.reconnectTimeoutId=setTimeout(function(){t.store&&t.passToStore("SOCKET_RECONNECT",t.reconnectionCount),t.connect(t.connectionUrl,t.opts),t.onEvent()},this.reconnectionDelay)):this.store&&this.passToStore("SOCKET_RECONNECT_ERROR",!0)}},{key:"onEvent",value:function(){var t=this;["onmessage","onclose","onerror","onopen"].forEach(function(e){t.WebSocket[e]=function(n){s.default.emit(e,n),t.store&&t.passToStore("SOCKET_"+e,n),t.reconnection&&"onopen"===e&&(t.opts.$setInstance(n.currentTarget),t.reconnectionCount=0),t.reconnection&&"onclose"===e&&t.reconnect()}})}},{key:"passToStore",value:function(t,e){this.passToStoreHandler?this.passToStoreHandler(t,e,this.defaultPassToStore.bind(this)):this.defaultPassToStore(t,e)}},{key:"defaultPassToStore",value:function(t,e){if(t.startsWith("SOCKET_")){var n="commit",o=t.toUpperCase(),r=e;"json"===this.format&&e.data&&(r=JSON.parse(e.data),r.mutation?o=[r.namespace||"",r.mutation].filter(function(t){return!!t}).join("/"):r.action&&(n="dispatch",o=[r.namespace||"",r.action].filter(function(t){return!!t}).join("/"))),this.mutations&&(o=this.mutations[o]||o),this.store[n](o,r)}}}]),t}();e.default=c}])});