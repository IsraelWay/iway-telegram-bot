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


output.markdown("Отправка справки")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

output.clear();

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}
if (!record.getCellValue("Справка консульская") || record.getCellValue("Справка консульская").length == 0) {
    output.markdown("Сначала загрузите справку (pdf file) в соответстующую ячейку");
    return;
}
if (!record.getCellValue("Есть справка")) {
    output.markdown("Сначала отметьте, что справка есть");
    return;
}


// инфо по консульству
let city = await base.getTable("Города").selectRecordAsync(record.getCellValue("Город")[0].id);
if (!city) {
    output.markdown("Не указан город, а надо в письме указать, где консульство");
    return;
}

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";

for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "report-ua") {
       email_html = template.getCellValueAsString("Html");
       break;
   }
}

output.clear();
output.markdown(`## Отправка справки для ${record.name} из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)

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

// запрос
let response = await fetch(host + '/report-ua', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: JSON.stringify({
      email: record.getCellValueAsString("Email"),
      full_name: record.getCellValueAsString("Info"),
      email_html: email_html,
      report_ua_url: record.getCellValue("Справка консульская")[0].url,
      id_record: record.id,
      tg_id: record.getCellValueAsString("tg_id")
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
    '(auto) справка отправлена (Украина)': new Date(),
});

output.clear();
output.markdown(`### Справка успешно отправлена ${record.getCellValueAsString("Info")}`);