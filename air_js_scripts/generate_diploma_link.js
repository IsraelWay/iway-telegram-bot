// Functions
function formatDate(isoDate) {
    if (!isoDate) return null;
    let date = new Date(isoDate);
    return date.toLocaleDateString("en-US", { month: "long", day: "2-digit", year: "numeric" });
}

function generateCertificateNumber(group, groupNumber) {
    let groupStr = String(group).padStart(3, "0"); // Делаем минимум 3 цифры, добавляя нули слева
    let groupNumberStr = String(groupNumber).padStart(3, "0"); // Делаем минимум 3 цифры
    return groupStr + groupNumberStr;
}

function encodeQueryParams(params) {
    return Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join("&");
}

// Tables
let participants = base.getTable("Участники"); // Таблица Участники
let programsTable = base.getTable("Программы");      // Таблица Программы
let templatesTable = base.getTable("Шаблоны программ"); // Таблица Шаблоны программ

// Participant
let record = await input.recordAsync('',participants).catch()
if (!record) {
    output.markdown("Запись на найдена, напишите Илюше");
    return;
}

// Set link to null
await participants.updateRecordAsync(record.id, {
    "Print diploma link": "",
    "Diploma link updated": new Date()
});


// Programm
let programId = record.getCellValue("Программа");
if (!programId) {
    console.log(record);
    output.text("Ошибка: У участника не указана Программа.");
    return;
}

let program = await programsTable.selectRecordAsync(programId[0].id);
if (!program) {
    console.log(programId);
    output.text("Ошибка: Программа не найдена.");
    return;
}

// Programm template
let templateId = program.getCellValue("Официальная программа");
if (!templateId) {
    console.log(program);
    output.text("Ошибка: У программы не указан Шаблон программы.");
    return;
}

let template = await templatesTable.selectRecordAsync(templateId[0].id);
if (!template) {
    console.log(templateId);
    output.text("Ошибка: Шаблон программы не найден.");
    return;
}

// Data
let participantName = record.getCellValue("Имя участника");
let participantGroup = record.getCellValue("Группа");
let participantNumber = record.getCellValue("Номер в группе");
let startDate = formatDate(program.getCellValue("Start date"));
let endDate = formatDate(program.getCellValue("End date"));
let dateRange = startDate && endDate ? `${startDate} - ${endDate}` : null;
let diplomaText = template.getCellValue("Текст диплома");
let printLink = template.getCellValue("Ссылка на печать диплома");

// Validate data
let missingFields = [];
if (!participantName) missingFields.push("Имя участника");
if (!diplomaText) missingFields.push("Текст диплома");
if (!printLink) missingFields.push("Ссылка на печать диплома");
if (!dateRange) missingFields.push("Дата начала и окончания программы (Start date / End date)");
if (!endDate) missingFields.push("End date");
if (!participantNumber) missingFields.push("Номер в группе");
if (!participantGroup) missingFields.push("Группа");
if (missingFields.length > 0) {
    output.text("Ошибка: Не заполнены следующие поля:\n" + missingFields.join(", "));
    return;
}

// Transform data
if (diplomaText && dateRange) {
    diplomaText = diplomaText.replace("[dateRange]", dateRange);
}
let certificateNumber;
let participantGroupName = participantGroup[0].name;
if (participantGroupName && participantNumber) {
    certificateNumber = "Certificate number: " + generateCertificateNumber(participantGroupName, participantNumber);
}

// Participant final data
let resultData = {
    "participantName": participantName,
    "diplomaText": diplomaText,
    "diplomaPrintLink": printLink,
    "dateRange": dateRange,
    "groupNumber": participantNumber,
    "groupName": participantGroupName,
    "endDate": endDate,
    "certificateNumber": certificateNumber
};
console.log("✅ Данные участника:", resultData);

// Generate link
let queryParams = encodeQueryParams({
    participantName: participantName,
    diplomaText: diplomaText,
    date: endDate || "",
    certificateNumber: certificateNumber || ""
});

let finalUrl = `${printLink}?${queryParams}`;
console.log("✅ Final URL:", finalUrl);

// Update new link
await participants.updateRecordAsync(record.id, {
    "Print diploma link": finalUrl,
    "Diploma link updated": new Date()
});