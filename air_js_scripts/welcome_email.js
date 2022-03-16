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

// предпочтительные даты
let inputConfig = input.config();
let preferred_dates =
    base.getTable("Leads").getField("prefer_dates").options.choices.map(option => option.name).join(", ");

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "welcome") {
       email_html = template.getCellValueAsString("Html");
       break;
   }
}

// запрос
let response = await fetch(host + '/welcome', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: JSON.stringify({
      email: inputConfig.email,
      email_html: email_html,
      full_name: inputConfig.full_name,
      id_record: inputConfig.id_record,
      preferred_dates: preferred_dates
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

console.log(`Done`);
