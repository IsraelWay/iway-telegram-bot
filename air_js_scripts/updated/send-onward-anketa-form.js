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


output.markdown("Отправка анекты Onward")
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
if (record.getCellValueAsString("target") != "onward") {
    output.markdown("Направление не Onward (" + record.getCellValueAsString("target") + ")");
    return;
}

let onward_form_from_lead = record.getCellValue("Onward анкета");
let onward_form_id = null;
let onward_forms_table = base.getTable("Onward анкеты");

if (!onward_form_from_lead) {
    onward_form_id = await onward_forms_table.createRecordAsync({
        'Lead': [{id: record.id}],
    });
}
else {
    onward_form_id = onward_form_from_lead[0].id;
}
let onward_form = await onward_forms_table.selectRecordAsync(onward_form_id);
if (!onward_form) {
    output.clear();
    output.markdown("## Не найден объект onward-анкеты для " + record.getCellValueAsString("Info"));
    return;
}

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
let email_picture = "";
for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "anketa_onward") {
       email_html = template.getCellValueAsString("Html");
       email_picture = template.getCellValueAsString("picture_url");
       break;
   }
}

output.clear();
output.markdown(`## Отправка анкеты Onward для ${record.name} (${record.getCellValueAsString("Email")}) из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)
if (record.getCellValueAsString("(auto) отправка анкеты onward")) {
    output.markdown("### Письмо с анкетой Onward уже ранее отправляли " + record.getCellValueAsString("(auto) отправка анкеты onward"));
}


let shouldContinue = await input.buttonsAsync(
    'Отправляем?',
    [
        {label: 'Отмена', value: 'cancel', variant: 'danger'},
        {label: 'Да, вперед, отправить анкету Onward', value: 'yes', variant: 'primary'},
    ],
);
if (shouldContinue === 'cancel') {
    output.clear();
    output.text('Отменено');
    return;
}

let actions = {
          "bottom" : {
            "link": onward_form.getCellValueAsString("link_to_edit_record"),
            "text": "Заполнить анкету Onward"
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
      email_picture: "https://static.tildacdn.com/tild6631-3136-4364-a433-646365623737/download.jpg",
      actions: actions,
      main_title: "Анкета на программу Onward",
      subject: "IsraelWay team - Анкета на программу Onward",
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
    '(auto) отправка анкеты onward': new Date(),
});

output.clear();
output.markdown(`### Анкета (${record.getCellValueAsString('target')}) успешно отправлена`);
