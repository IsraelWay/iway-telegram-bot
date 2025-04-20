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


output.markdown("Отправка запроса на документы для онварда")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

output.clear();

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}

if (record.getCellValueAsString("target") != "onward") {
    output.markdown("## Чет не то! Направление не Onward");
    return;
}

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
let email_picture = ""

for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "onward-docs") {
       email_html = template.getCellValueAsString("Html");
       email_picture = template.getCellValueAsString("picture_url");
       break;
   }
}

output.clear();
output.markdown(`## Отправка заропса документов для Onward для ${record.name} (${record.getCellValueAsString("Email")}) из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)

let shouldContinue = await input.buttonsAsync(
    'Отправляем?',
    [
        {label: 'Отмена', value: 'cancel', variant: 'danger'},
        {label: 'Да, вперед, отправить запрос участнику', value: 'yes', variant: 'primary'},
    ],
);
if (shouldContinue === 'cancel') {
    output.clear();
    output.text('Отменено');
    return;
}

let actions = {
    "top" : {
        "link": record.getCellValueAsString("link_to_upload_onward_check_docs"),
        "text": "Загрузить документы"
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
      main_title: "Документы на Onward",
      subject: "IsraelWay team - документы на Onward",
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
    '(auto) отправка письма о доках на онвадр': new Date(),
});

output.clear();
output.markdown(`### Запрос на документы Onward успешно отправлен ${record.getCellValueAsString("Info")}`);
