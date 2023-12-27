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

output.clear();
output.markdown(`## Отправка подтверждения автоэкскурсии на ${record.getCellValueAsString("Email")}`);
output.markdown(`### Письмо будет содержать:`);
output.markdown(record.getCellValueAsString("Email html"));
output.markdown(`### И кнопку: Данные о заявке тут с ссылкой ` + record.getCellValueAsString("Ссылка для просмотра"));

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


let data4Table = [
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
        "name": "Промокоды (водитель + пассажиры):",
        "value": [
            record.getCellValueAsString("Промокод водителя"),
            record.getCellValueAsString("Промокод пассажир 1"),
            record.getCellValueAsString("Промокод пассажир 2"),
            record.getCellValueAsString("Промокод пассажир 3"),
            record.getCellValueAsString("Промокод пассажир 4")
        ].join("<br/>")
    },
    {
        "name": "Дополнительная информация:",
        "value":
            record.getCellValueAsString("Заметки для участников")
    }
];
let tableMarkup = data4Table.map(function(item) {
    return "<tr>" +
                "<td style='width: 50%; padding: 5px; text-align: left; vertical-align: top; background-color: #f7f8fc; color: #333; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold;'>" + item.name + "</td>" +
                "<td style='width: 50%; padding: 5px; text-align: left; vertical-align: top; background-color: #f7f8fc; color: #333; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold;'>" + item.value + "</td>" +
            "</tr>"
}).join("");

tableMarkup = '<table cellspacing="2" cellpadding="10" border="0" style="border-collapse: collapse;">' + tableMarkup + "</table>";

// запрос
let response = await fetch(host + '/send-email', {
  method: 'POST',
  headers: {
      "Authorization": 'Bearer ' + token,
      "Content-Type": "application/json"
  },
  body: JSON.stringify({
      email: "ipolo.box@gmail.com",// record.getCellValueAsString("Email"),
      full_name: record.getCellValueAsString("Email full name"),
      email_html: record.getCellValueAsString("Email html") + tableMarkup,
      email_picture: "https://static.tildacdn.com/tild3036-3731-4331-b837-613537663963/Screenshot_2023-12-2.png",
      actions: {
          "top" : {
            "link": record.getCellValueAsString("Ссылка для просмотра"),
            "text": "Данные о заявке тут"
        },
      },
      main_title: "Подтверждение заявки на автоэкскурсию",
      subject: "IsraelWay team - подтверждение заявки на автоэкскурсию",
      id_record: record.id,
      cc: "ilya@autoproof.dev",
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

await autoRequests.updateRecordAsync(record, {
    '(auto) дата отправки подтверждения': new Date(),
});

output.clear();
output.markdown(`### Подтверждение заявки на автоэкскурсию отправлено успешно`);
