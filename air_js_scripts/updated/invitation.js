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


output.markdown("Отправка приглашения")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

output.clear();

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}
if (record.getCellValueAsString("target") != "masa") {
    output.markdown("## Действие может быть только для программ Маса, сообщие Илье, что было это сообщение (лучше сделать скриншот)");
    return;
}
if (!record.getCellValue("Первичное интервью")) {
    output.markdown("Первичное интервью не пройдено");
    return;
}
if (record.getCellValueAsString("consul_check") == "Пройдена") {
    output.markdown("Проверка уже пройдена");
    return;
}
if (!record.getCellValue("Приглашение") || record.getCellValue("Приглашение").length == 0) {
    output.markdown("Сначала загрузите пришлашение (pdf file) в соответстующую ячейку");
    return;
}

if (!record.getCellValue("Город")) {
    output.markdown("Укажите город");
    return;
}

// инфо по консульству
let city = await base.getTable("Города").selectRecordAsync(record.getCellValue("Город")[0].id);
if (!city) {
    output.markdown("Не указан город, а надо в письме указать, где консульство");
    return;
}
let consul_info = city.getCellValueAsString("Данные по консульствам") ?
    city.getCellValueAsString("Данные по консульствам"):
    city.getCellValueAsString("(страна) Данные по консульствам");

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";

let postfix = "";
if (["Украина"].includes(city.getCellValueAsString("Страна"))) {
    postfix += "-ua";
}

for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "invitation-letter" + postfix) {
       email_html = template.getCellValueAsString("Html");
       break;
   }
}

output.clear();
output.markdown(`## Отправка приглашения для ${record.name} из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)

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
        "link": record.getCellValueAsString("link_to_form_for_consul_check_date"),
        "text": "Указать дату проверки"
    },
    "subbottom" : {
        "link": record.getCellValueAsString("link_to_mark_counsul_check"),
        "text": "Указать, что проверка пройдена"
    }
};

let invitation_files = record.getCellValue("Приглашение");
let files = [];
if (invitation_files) {
    for (let file of invitation_files) {
        files.push({
            filename: file.filename,
            url: file.url
        });
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
      email_html: email_html + "<br/>" + consul_info,
      actions: actions,
      main_title: "Итак, консульская проверка!",
      subject: "IsraelWay team - консульская проверка!",
      id_record: record.id,
      attachments: files,
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
    '(auto) отправка приглашения': new Date(),
});

output.markdown(`### Приглашение и письмо с инструкциями успешно отправлены ${record.getCellValueAsString("Info")}`);
