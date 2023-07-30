const host = 'localhost';
const port = 50008;

const botName = 'matbot';
const safetyRegexp = /^[0-9 .+\-*/()]+$/;
const config = {
  family: 4,
  port: port,
  host: host,
};
const net = require('node:net');
const client = net.createConnection(config, () => {
  console.log(`connected to server as ${botName}`);
});
client.on('end', () => {
  console.log('disconnected from server');
});
client.on('data', data => {
  var text = data.toString();
  var splitText = text.split(':', 1);
  var user = splitText[0];
  var message = text.slice(user.length + 2);
  if (message.startsWith(`${botName}: `)) {
    message = message.slice(botName.length + 2).toString();
    console.log(`user "${user}" wrote "${message}"`);
    if (safetyRegexp.exec(message)) {
      try {
        var result = eval(message);
        client.write(`${botName}: ${user}: ${message} = ${result}`);
      } catch (error) {
        console.log(error);
        client.write(`${botName}: ${user}: Noget gik galt.`);
      }
    } else {
      console.log('message might be unsafe, ignoring');
      client.write(`${botName}: ${user}: Det er vist ikke et rigtigt regnestykke.`);
    }
  }
});
