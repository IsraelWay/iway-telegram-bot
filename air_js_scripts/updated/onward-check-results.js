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


output.markdown("###  Отправка результатов Onward проверки")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()
if (!record) {
    output.markdown("Записи нет - напишите Илюше");
    return;
}

if (record.getCellValueAsString("target") != "onward") {
    output.clear();
    output.markdown("### Направление (target) не Onward");
    return;
}

output.clear();

let onwardCheckResult = await input.buttonsAsync(
    `Результаты проверки документов на Onward для ${record.getCellValueAsString("Info")}`,
    [
        {label: 'Проверка не пройдена', value: 'no', variant: 'danger'},
        {label: 'Проверка пройдена успешно', value: 'yes', variant: 'primary'},
    ],
);
let reasons = "";
if (onwardCheckResult === 'no') {
    reasons = await input.textAsync("Укажите причины и что надо сделать, для успешного прохождения проверки");
}


// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
let email_picture = "";

for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "onward-docs-check-" + onwardCheckResult) {
       email_html = template.getCellValueAsString("Html");
       email_picture = template.getCellValueAsString("picture_url");
       break;
   }
}

output.clear();
output.markdown(`## Отправка ${record.name} (${record.getCellValueAsString("Email")})") информации о результатах проверки онвард:`);
output.table([
    ['Пройдена', onwardCheckResult],
    ['Причины', reasons],
    ['Кому', record.name],
    ['Куда', record.getCellValueAsString("Email")],
]);

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

let actions = {};
if (onwardCheckResult != "yes") {
    actions = {
        "top" : {
            "link": record.getCellValueAsString("link_to_upload_onward_check_docs"),
            "text": "Обновить документы"
        }
    }
}

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
      email_html: email_html + reasons,
      actions: actions,
      main_title: "Результаты проверки Onward",
      subject: "IsraelWay team - результаты проверки Onward",
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
    '(auto) результаты проверки письмо': new Date(),
});

output.clear();
output.markdown(`### Результаты проверки онвард отправлены ${record.getCellValueAsString("Info")}. ${reasons}`);
