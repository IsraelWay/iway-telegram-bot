// Server access
let creds = base.getTable('Techdata');
let host, token = null;
let servers = await creds.selectRecordsAsync();
for (let server of servers.records) {
   if (server.getCellValue("Active")) {
       host = server.getCellValueAsString("host");
       token = server.getCellValueAsString("token");
       break;
   }
}
if (!host || !token) {
    output.markdown("Не задан доступ до сервера");
    return;
}
output.markdown("Connecting to: " + host);
// end server access


output.markdown("Отправка на почту ссылки на анкету")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}
if (!record.getCellValue("Первичное интервью")) {
    output.markdown("Первичное интервью не пройдено");
    return;
}
if (!record.getCellValue("target")) {
    output.markdown("Не указан target - направление, куда хочет лид");
    return;
}

let link = record.getCellValueAsString("target") == "onward" ?
    "https://web.miniextensions.com/0xDnvFzxiNW1okIC8bJB":
    "https://web.miniextensions.com/K3pC5QWCpRHcntwO6n63";
link += "?prefill_Lead=" + record.id;


let response = await fetch(host + '/anketa', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: JSON.stringify({
      email: record.getCellValueAsString("Email"),
      anketa_link: link,
      full_name: record.getCellValueAsString("Info")
  })
})
.catch( error => {
    output.markdown("Ошибка соединения: " + error);
    output.inspect(error)
});

// Response
let data = await response.json();
if (!data.result) {
    output.markdown("## Не успех: " + data.message);
    output.inspect(data);
    return;
}

output.markdown(`### Анкета (${record.getCellValueAsString('target')}) успешно отправлена`);
