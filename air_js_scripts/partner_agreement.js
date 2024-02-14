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


output.markdown("Отправить договор на подпись")
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
let email_picture = "";
for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "partners_agreement") {
       email_html = template.getCellValueAsString("Html");
       email_picture = template.getCellValueAsString("picture_url");
       break;
   }
}

// Ссылка на просмотр договора
let settings = await base.getTable("Settings").selectRecordsAsync();
let partners_agreement_template_link = "";
let upload_partner_agreement_link = "";
for (let key of settings.records) {
   if (key.getCellValueAsString("key") == "partners_agreement") {
       partners_agreement_template_link = key.getCellValueAsString("link");
   }
   if (key.getCellValueAsString("key") == "upload_partner_agreement_link") {
       upload_partner_agreement_link = key.getCellValueAsString("value");
   }

}

output.clear();
output.markdown(`## Отправка `);
output.markdown(`### Отправляем договор на подписание ` + record.getCellValueAsString("Name") + " на " + record.getCellValueAsString("Email"));

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
          "top" : {
            "link": record.getCellValueAsString("Ссылка на договор"),
            "text": "Подписать договор"
          },
          "bottom" : {
            "link": upload_partner_agreement_link + record.id,
            "text": "Загрузить договор"
          },
          "subbottom" : {
            "link": partners_agreement_template_link,
            "text": "Отдельно просмотреть текст договора"
          },
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
      full_name: record.getCellValueAsString("Полное имя"),
      email_html: email_html,
      email_picture: email_picture ? email_picture : "https://static.tildacdn.com/tild3036-3731-4331-b837-613537663963/Screenshot_2023-12-2.png",
      actions: actions,
      main_title: "Подписание договора",
      subject: "IsraelWay team - договор для агента/партнера",
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
    '(auto) дата отправки договора': new Date(),
});

output.clear();
output.markdown(`### Договор на подпись отправлен`);
