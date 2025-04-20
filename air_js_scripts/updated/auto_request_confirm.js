// Server access
let creds = base.getTable('Techdata');
let host, token, cc = null;
let servers = await creds.selectRecordsAsync();
for (let server of servers.records) {
   if (server.getCellValue("Active")) {
       host = server.getCellValueAsString("host");
       token = server.getCellValueAsString("token");
       cc = server.getCellValueAsString("CC for excursion requests ");
       break;
   }
}
if (!host || !token) {
    output.markdown("Не задан доступ до сервера");
    return;
}
output.markdown("Connecting to: " + host);
// end server access


output.markdown("Подтверждение автозаявки")
let autoRequests = base.getTable("Заявки на автоэкскурсии");
let record = await input.recordAsync('',autoRequests).catch()

output.clear();

if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}

// тело письма
let email_templates_base = record.getCellValueAsString("Email html");

let data4Table = [
    {
        "name": "Номер заявки",
        "value": record.getCellValueAsString("Номер заявки")
    },
    {
        "name": "Название экскурсии:",
        "value": record.getCellValueAsString("Название экскурсии")
    },
    {
        "name": "Дата и время:",
        "value": record.getCellValueAsString("Дата начала")
    },
    {
        "name": "Время заказа машины:",
        "value": record.getCellValueAsString("Время заказа машины")
    },
    {
        "name": "Водитель:",
        "value": record.getCellValueAsString("Водитель")
    },
    {
        "name": "Пассажиры",
        "value": record.getCellValueAsString("Дополнительные участники")
    },
    {
        "name": "Промокоды (водитель + пассажиры):",
        "value": [
            "1: " + record.getCellValueAsString("Промокод водителя"),
            "2: " + record.getCellValueAsString("Промокод пассажир 1"),
            "3: " + record.getCellValueAsString("Промокод пассажир 2"),
            "4: " + record.getCellValueAsString("Промокод пассажир 3"),
            "5: " + record.getCellValueAsString("Промокод пассажир 4")
        ].join("<br/>")
    },
    {
        "name": "Дополнительная информация:",
        "value":
            record.getCellValueAsString("Заметки для участников")
    },
    {
        "name": "Статус:",
        "value": record.getCellValueAsString("Статус")
    },
];

let tableMarkup = data4Table.map(function(item) {
    return "<tr>" +
                "<td style='width: 50%; padding: 5px; text-align: left; vertical-align: top; background-color: #f7f8fc; color: #333; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold;'>" + item.name + "</td>" +
                "<td style='width: 50%; padding: 5px; text-align: left; vertical-align: top; background-color: #f7f8fc; color: #333; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold;'>" + item.value + "</td>" +
            "</tr>"
}).join("");

tableMarkup = '<table cellspacing="2" cellpadding="10" border="0" style="border-collapse: collapse;">' + tableMarkup + "</table>";



output.clear();
output.markdown(`## Отправка подтверждения автоэкскурсии на ${record.getCellValueAsString("Email")}`);

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
output.clear();

let vaucherAttachment = record.getCellValue("Ваучеры (аренда машины + входы)");
let files = [];
if (vaucherAttachment) {
    for (let file of vaucherAttachment) {
        files.push({
            filename: file.filename,
            url: file.url
        });
    }
}

let dataString = JSON.stringify({
      email: record.getCellValueAsString("Email"),
      full_name: record.getCellValueAsString("Email full name"),
      email_html: record.getCellValueAsString("Email html") + tableMarkup,
      email_picture: "https://static.tildacdn.com/tild3036-3731-4331-b837-613537663963/Screenshot_2023-12-2.png",
      actions: {},
      main_title: "Подтверждение заявки на автоэкскурсию",
      subject: "IsraelWay team - подтверждение заявки на автоэкскурсию",
      id_record: record.id,
      attachments: files,
      tg_id: ""//record.getCellValueAsString("tg_id")
  });
// запрос
let response = await fetch(host + '/send-email', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: dataString
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
console.log(data);

await autoRequests.updateRecordAsync(record, {
    '(auto) дата отправки подтверждения': new Date(),
});

// output.clear();
output.markdown(`### Подтверждение заявки на автоэкскурсию отправлено успешно`);
