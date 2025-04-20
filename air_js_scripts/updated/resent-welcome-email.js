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


output.markdown("Повторная отправка Welcome email")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}


// предпочтительные даты
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

let actions = {
    "bottom" : {
        "link": record.getCellValueAsString("link_to_form_from_welcome_email"),
        "text": "Заполнить"
    }
};


// запрос
let response = await fetch(host + '/send-email', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: JSON.stringify({
      email: record.getCellValueAsString("Email"),
      full_name: record.getCellValueAsString("Info"),
      email_html: email_html,
      actions: actions,
      main_title: "Привет, " + record.getCellValueAsString("Info") + "!",
      subject: "IsraelWay team - Welcome!",
      id_record: record.id,
      tg_id: ""//record.getCellValueAsString("tg_id")
  })
})
.catch( error => {
    output.markdown("Ошибка соединения: " + error);
    output.inspect(error)
});

// Response
let data = await response.json();
if (!data.result) {
    console.log("## Не успех: " + data.message);
    console.log(data);
    return;
}

await leads.updateRecordAsync(record.id, {
    '(auto) дата отправки welcome email': new Date(),
});

console.log(`Done`);
