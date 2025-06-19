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


output.markdown("Отправка анекты на залоги")
let leads = base.getTable("Участники");
let record = await input.recordAsync('',leads).catch()

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}

let deposit_refund_id = null;
let deposit_refunds = record.getCellValue("Анкета на залоги");
let deposit_refund_table = base.getTable("Анкета на залоги");
if (!deposit_refunds) {
    deposit_refund_id = await deposit_refund_table.createRecordAsync({
        'Участник': [{id: record.id}],
    });
}
else {
    deposit_refund_id = deposit_refunds[0].id;
}

let deposit_refund_obj = await deposit_refund_table.selectRecordAsync(deposit_refund_id);
if (!deposit_refund_obj) {
    output.clear();
    output.markdown("## Не найден объект анкеты на залоги для " + record.getCellValueAsString("Info"));
    return;
}

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "anketa_for_zalogs") {
       email_html = template.getCellValueAsString("Html");
       break;
   }
}

output.clear();
output.markdown(`## Отправка анкеты на залог ${record.name} (${record.getCellValueAsString("Email")})`)
if (record.getCellValueAsString("(auto) отправка анкеты на залоги")) {
    output.markdown("### Письмо с анкетой на залоги уже ранее отправляли " + record.getCellValueAsString("(auto) отправка анкеты на залоги"));
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
        "link": deposit_refund_obj.getCellValueAsString("link_to_from"),
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
      full_name: record.getCellValueAsString("Имя + инфо"),
      email_html: email_html,
      email_picture: "https://static.tildacdn.com/tild6631-3136-4364-a433-646365623737/download.jpg",
      actions: actions,
      main_title: "Анкета на залоги",
      subject: "IsraelWay team - анкета залоги",
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
    '(auto) отправка анкеты на залоги': new Date(),
});

output.clear();
output.markdown(`### Анкета (${record.getCellValueAsString('Имя участника')}) на залоги успешно отправлена`);
