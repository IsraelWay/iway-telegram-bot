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


output.markdown("Отправка дат прилета")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()
if (!record) {
    output.markdown("Записи нет - напишите Илюше");
    return;
}

if (!record.getCellValueAsString("Ориентировочные даты прилета")) {
    output.markdown("## Не указаны ориентировочные даты прилета");
    return;
}

output.clear();

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
let email_picture = "";

for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "avia-dates") {
       email_html = template.getCellValueAsString("Html");
       email_picture = template.getCellValueAsString("picture_url");
       break;
   }
}

output.clear();
output.markdown(`## Отправка дат прилета ${record.getCellValueAsString("Ориентировочные даты прилета")} для ${record.name} (${record.getCellValueAsString("Email")}) из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)

let shouldContinue = await input.buttonsAsync(
    'Отправляем?',
    [
        {label: 'Отмена', value: 'cancel', variant: 'danger'},
        {label: 'Да, вперед', value: 'yes', variant: 'primary'},
    ],
);
if (shouldContinue === 'cancel') {
    output.clear();
    output.text('Отменено');
    return;
}

let actions = {
    "bottom" : {
        "link": record.getCellValueAsString("link_to_upload_avia_tickets"),
        "text": "Загрузить билеты"
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
      email_html: email_html + record.getCellValueAsString("Ориентировочные даты прилета"),
      main_title: "Согласованные даты прилета",
      subject: "IsraelWay team - даты прилета",
      actions: actions,
      email_picture: email_picture,
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
    output.markdown("## Не успех: " + data.message);
    output.inspect(data);
    return;
}

await leads.updateRecordAsync(record, {
    '(auto) отправка согласованных дат прилета': new Date(),
});

output.clear();
output.markdown(`### Даты ${record.getCellValueAsString("Ориентировочные даты прилета")} отправлены ${record.getCellValueAsString("Info")}`);
