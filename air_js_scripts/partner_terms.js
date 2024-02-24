// Server access
let creds = base.getTable('Techdata');
let host, token, cc = null;
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


output.markdown("Отправить агенту условия")
let agentsTable = base.getTable("Агенты");
let record = await input.recordAsync('',agentsTable).catch()

output.clear();

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
let email_markdown = "";
let email_picture = "";
for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "partners_agreement_terms") {
       email_html = template.getCellValueAsString("Html");
       email_markdown = template.getCellValueAsString("Текст письма");
       email_picture = template.getCellValueAsString("picture_url");
       break;
   }
}

output.clear();
output.markdown(`## Отправка `);
output.markdown(`### Отправляем условия для агента ` + record.getCellValueAsString("Name") + " на " + record.getCellValueAsString("Email"));
output.markdown(email_markdown);

await input.buttonsAsync(
    'Помимо этих условий укажите дополнительные расценки партнерства:',
    [
        {label: 'Указать', value: 'yes', variant: 'primary'},
    ],
);
output.clear();
let custom_terms = await input.textAsync('Введите дополнительные условия:');

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

let personal_link_info = "Чтобы система поняла, что участник пришел от тебя, добавляй к каждой! ссылке свой уникальный реферальный код: <br/>" + record.getCellValueAsString("Что добавить к ссылке на любую программу");
// запрос
let response = await fetch(host + '/send-email', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: JSON.stringify({
      email: record.getCellValueAsString("Email"),
      full_name: record.getCellValueAsString("Полное имя"),
      email_html: email_html + custom_terms + "<br/>" + personal_link_info,
      email_picture: email_picture ? email_picture : "https://static.tildacdn.com/tild3036-3731-4331-b837-613537663963/Screenshot_2023-12-2.png",
      actions: {
          "bottom" : {
            "link": "https://israelway.ru/masa-mix" + record.getCellValueAsString("Что добавить к ссылке на любую программу"),
            "text": "Пример персональной ссылки на программу Mix"
          },
          "subbottom" : {
            "link": "https://israelway.ru/onward-experience-2" + record.getCellValueAsString("Что добавить к ссылке на любую программу"),
            "text": "Пример персональной ссылки на Onward"
          },
      },
      main_title: "Расценки партнерства",
      subject: "IsraelWay team - расценки партнерства",
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

await agentsTable.updateRecordAsync(record, {
    '(auto) дата отправки расценок': new Date(),
});

output.clear();
output.markdown(`### Расценки и условия отправлены`);
