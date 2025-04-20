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


output.markdown("Отправка договора")
let leads = base.getTable("Leads");
let record = await input.recordAsync('',leads).catch()

output.clear();

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}

if (record.getCellValue("Текст договора")?.length == null) {
    output.markdown("Не указан текст договора (загрузите файл)");
    return;
}

if (!record.getCellValue("Start date (from Предпочитаемая программа)")
        || !record.getCellValue("End date (from Предпочитаемая программа)")) {
    output.markdown("Не заданы даты программы");
    return;
}

let fill_agreement_url = record.getCellValueAsString("Договор форма (from Официальная программа)");
let prefill_uri = [];
prefill_uri.push("fio=" + record.getCellValueAsString("Имя") + " " + record.getCellValueAsString("Фамилия"));
prefill_uri.push("passport=" + record.getCellValueAsString("Номер загран. паспорта"));
prefill_uri.push("address=" + record.getCellValueAsString("Страна (from Город)") + ", " + record.getCellValueAsString("Город") + ", " + record.getCellValueAsString("Адрес проживания"));
prefill_uri.push("mother_phone=" + record.getCellValueAsString("Телефон матери"));
prefill_uri.push("father_phone=" + record.getCellValueAsString("Телефон отца"));
prefill_uri.push("email=" + record.getCellValueAsString("Email"));
prefill_uri.push("dates=" +
        new Date(record.getCellValue("Start date (from Предпочитаемая программа)"))
        .toLocaleString("ru-RU", { year: 'numeric', month: 'numeric', day: 'numeric'})
         + " до " +
         new Date(record.getCellValue("End date (from Предпочитаемая программа)"))
         .toLocaleString("ru-RU", { year: 'numeric', month: 'numeric', day: 'numeric'}));


prefill_uri.push("friend_phone=" + record.getCellValueAsString("Имя и телефон доверенного лица для экстренной связи"));

if (record.getCellValueAsString("Официальная программа (from Предпочитаемая программа)") == "Mix") {
    let programText = await input.textAsync('Укажите содержание программы MIX');
    let studyText = await input.textAsync('Укажите содержание учебы MIX');
    prefill_uri.push("program_text=" + programText);
    prefill_uri.push("study_text=" + studyText);

    output.text("Длина содержания программы + содержани учебы: " + (programText.length + studyText.length) + " символов");
}

let prefill_uri_print = prefill_uri;
prefill_uri = prefill_uri.map((item) => item.replace(/(?:\\[rn]|[\r\n]+)+/g, " "));

// output.clear();
// output.inspect(prefill_uri);
// output.markdown(fill_agreement_url + "?" + prefill_uri.join("&"));
// return;

// тело письма
let email_templates_base = base.getTable("Шаблоны писем");
let email_templates = await email_templates_base.selectRecordsAsync();
let email_html = "";
let email_picture = "";

for (let template of email_templates.records) {
   if (template.getCellValueAsString("Название письма") == "agreement") {
       email_html = template.getCellValueAsString("Html");
       email_picture = template.getCellValueAsString("picture_url");
       break;
   }
}

// output.clear();
let linkLength = (fill_agreement_url + "?" + prefill_uri.join("&")).length;
if (linkLength >= 610) {
    output.clear();
    if (record.getCellValueAsString("Официальная программа (from Предпочитаемая программа)") == "Mix") {
        output.markdown("## Слишком длинное содержание программы/учебы. Начните сначала и уменьшите текст на " + (linkLength - 610) + " символов");
        output.text("Детально: по указанным данным формируется личная ссылка на договор для лида. Длина ссылки на договор должна быть не более 610 символов (иначе не будет работать в почте yandex). У текущей ссылки: " + linkLength
                        + ". Чтобы отправить пиьсмо, начните сначала и уменьшите содержание Программы/Учебы для программ MIX на " + (linkLength - 610) + " символов. "
                        + "Важно: расчет ограничения на символы просиходит для каждого лида индивидуально, так как у всех разные адреса, имена, телефоны и другие данные.");
    }
    else {
        output.markdown("## Ссылка длинне, чем надо на " + (linkLength - 610) + " символов. Обратитесь к Илюше, сделав скриншот и указав на каком конкретно лиде и программе произошла ошибка.");
    }
    return;
}

output.markdown(`## Отправка договора ${record.name} из ${record.getCellValueAsString("Город")} ${record.getCellValueAsString("Страна (from Город)")}`)
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

let link_to_sign_form = fill_agreement_url + "?" + prefill_uri.map(encodeURI).join("&");


let actions = {
    "top" : {
        "link": link_to_sign_form,
        "text": "Подписать договор"
    },
    "bottom" : {
        "link": record.getCellValueAsString("link_to_upload_signed_agreement"),
        "text": "Загрузить подписанный договор"
    }
};

let agreement_text = record.getCellValue("Текст договора");
let files = [];
if (agreement_text) {
    for (let file of agreement_text) {
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
      email_html: email_html,
      main_title: "Договор",
      subject: "IsraelWay team - договор!",
      actions: actions,
      email_picture: email_picture,
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
    '(auto) договор отправлен': new Date(),
    'Индивидуальная ссылка на договор': link_to_sign_form
});

output.clear();
output.markdown(`### Договор успешно отправлен на подпись ${record.getCellValueAsString("Info")}`);
output.inspect(prefill_uri_print);
output.markdown(`## Индивидуальная ссылка на договор добавлена в соответствующее поле, а также вот [она](${link_to_sign_form})`);
