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


output.markdown("Отправка на почту плана + запроса на данные")
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

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "plan_" + record.getCellValueAsString("target")) {
       email_html = template.getCellValueAsString("Html");
       break;
   }
}

output.clear();
output.markdown(`## Отправка плана действий для ${record.name} (${record.getCellValueAsString("Email")}) из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)

let shouldContinue = await input.buttonsAsync(
    'Отправляем?',
    [
        {label: 'Отмена', value: 'cancel', variant: 'danger'},
        {label: 'Да, вперед, отправить план', value: 'yes', variant: 'primary'},
    ],
);
if (shouldContinue === 'cancel') {
    output.clear();
    output.text('Отменено');
    return;
}

let actions = {
    "top" : {
        "link": record.getCellValueAsString("link_to_form_for_detailed_data"),
        "text": "Заполнить данные о себе"
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
      email_picture: "https://static.tildacdn.com/tild3532-6638-4230-b134-626639323661/glenn-carstens-peter.jpg",
      actions: actions,
      main_title: "Отлично, ниже кнопка для заполнения данных о себе, а под ней - наш план!",
      subject: "IsraelWay team - детальный план",
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
    '(auto) отправка плана + запроса данных': new Date(),
});

output.clear();
output.markdown(`### План (${record.getCellValueAsString('target')}) успешно отправлен`);
