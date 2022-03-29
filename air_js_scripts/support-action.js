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
    console.log("Не задан доступ до сервера");
    return;
}
console.log("Connecting to: " + host);
// end server access

let inputConfig = input.config();
let lead = inputConfig.lead.length ? inputConfig.lead : null;
let email = lead ? inputConfig.email_from_lead[0] : inputConfig.semail;
let full_name = inputConfig.full_name;
let email_html = inputConfig.answer;

// support action
let action = "https://web.miniextensions.com/l5FVEWu0yjIkgQu2oj6V?"
let prefill_uri = [];
if (lead) {
  prefill_uri.push("prefill_Lead=" + lead);
}
prefill_uri.push("prefill_ФИО=" + full_name);
prefill_uri.push("prefill_email=" + email);
prefill_uri.push("prefill_Прошлый вопрос=" + inputConfig.id_request_record);
prefill_uri = prefill_uri.map(encodeURI);

// запрос
let response = await fetch(host + '/support-action', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: JSON.stringify({
      email: email,
      email_html: email_html,
      email_picture: "http://israelway.ru/wp-content/uploads/2022/03/hadija-saidi-jCfDzOQ2-C8-unsplash.jpg",
      support_action: action + prefill_uri.join("&"),
      full_name: full_name,
      id_record: lead,
      tg_id: inputConfig.tg_id
  })
})
.catch( error => {
    console.log("Ошибка соединения: " + error);
    console.log(error)
});

// Response
let data = await response.json();
if (!data.result) {
    console.log("## Не успех: " + data.message);
    console.log(data);
    return;
}

let emailRequests = base.getTable("EmailRequests");
await emailRequests.updateRecordAsync(inputConfig.id_request_record, {
    '(auto) oтправлен ответ': new Date(),
});

console.log(`Done`);
