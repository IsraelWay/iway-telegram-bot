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


output.markdown("Отправка анекты масы")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}
if (!record.getCellValue("target")) {
    output.markdown("Не указан target - направление, куда хочет лид");
    return;
}
if (record.getCellValueAsString("target") != "masa") {
    output.markdown("Направление не маса (" + record.getCellValueAsString("target") + ")");
    return;
}

let anketa = record.getCellValue("Анкета масы");
let anketa_id = null;
let ankets = base.getTable("Masa анкеты");
if (!anketa) {
    anketa_id = await ankets.createRecordAsync({
        'Lead': [{id: record.id}],
    });
}
else {
    anketa_id = anketa[0].id;
}

let ank_obj = await ankets.selectRecordAsync(anketa_id);
if (!ank_obj) {
    output.clear();
    output.markdown("## Не найден объект анкеты для " + record.getCellValueAsString("Info"));
    return;
}


// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "anketa_masa") {
       email_html = template.getCellValueAsString("Html");
       break;
   }
}

output.clear();
output.markdown(`## Отправка анкеты маса для ${record.name} (${record.getCellValueAsString("Email")}) из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)
if (record.getCellValueAsString("(auto) отправка анкеты маса")) {
    output.markdown("### Письмо с анкетой уже ранее отправляли " + record.getCellValueAsString("(auto) отправка анкеты маса"));
}


let shouldContinue = await input.buttonsAsync(
    'Отправляем?',
    [
        {label: 'Отмена', value: 'cancel', variant: 'danger'},
        {label: 'Да, вперед, отправить анкету', value: 'yes', variant: 'primary'},
    ],
);
if (shouldContinue === 'cancel') {
    output.clear();
    output.text('Отменено');
    return;
}

let actions = {
          "bottom" : {
            "link": ank_obj.getCellValueAsString("link_to_edit_record"),
            "text": "Заполнить анкету"
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
      full_name: record.getCellValueAsString("Info"),
      email_html: email_html,
      email_picture: "https://static.tildacdn.com/tild6631-3136-4364-a433-646365623737/download.jpg",
      actions: actions,
      main_title: "Анкеты на программу Маса",
      subject: "IsraelWay team - анкета на программу Маса",
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
    '(auto) отправка анкеты маса': new Date(),
});

output.clear();
output.markdown(`### Анкета (${record.getCellValueAsString('target')}) успешно отправлена`);
