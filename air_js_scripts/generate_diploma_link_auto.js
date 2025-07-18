// Functions
function formatDate(isoDate) {
    if (!isoDate) return null;
    let date = new Date(isoDate);
    return date.toLocaleDateString("en-US", { month: "long", day: "2-digit", year: "numeric" });
}

function generateCertificateNumber(group, groupNumber) {
    let groupStr = String(group).padStart(3, "0");
    let groupNumberStr = String(groupNumber).padStart(3, "0");
    return groupStr + groupNumberStr;
}

function encodeQueryParams(params) {
    return Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join("&");
}

// Получаем данные от Automation
let recordId = input.config().recordId;
if (!recordId) {
    console.log("Ошибка: ID записи не передан в Automation.");
    return;
}

// Tables
let participants = base.getTable("Участники");
let programsTable = base.getTable("Программы");
let templatesTable = base.getTable("Шаблоны программ");

// Получаем участника
let record = await participants.selectRecordAsync(recordId);
if (!record) {
    console.log("Ошибка: Участник не найден.");
    return;
}

// Сбрасываем старую ссылку и дату
await participants.updateRecordAsync(record.id, {
    "Print diploma link": "",
    "Diploma link updated": new Date()
});

// Получаем ID программы
let programId = record.getCellValue("Программа");
if (!programId) {
    console.log("Ошибка: У участника не указана Программа.");
    return;
}

let program = await programsTable.selectRecordAsync(programId[0].id);
if (!program) {
    console.log("Ошибка: Программа не найдена.");
    return;
}

// Получаем ID шаблона программы
let templateId = program.getCellValue("Официальная программа");
if (!templateId) {
    console.log("Ошибка: У программы не указан Шаблон программы.");
    return;
}

let template = await templatesTable.selectRecordAsync(templateId[0].id);
if (!template) {
    console.log("Ошибка: Шаблон программы не найден.");
    return;
}

// Данные участника
let participantName = record.getCellValue("Имя участника");
let participantGroup = record.getCellValue("Группа");
let participantNumber = record.getCellValue("Номер в группе");
let startDate = formatDate(program.getCellValue("Start date"));
let endDate = formatDate(program.getCellValue("End date"));
let dateRange = startDate && endDate ? `${startDate} - ${endDate}` : null;
let personalDiplomaText = record.getCellValue("Personal diploma text");
let diplomaText = personalDiplomaText ? personalDiplomaText : template.getCellValue("Текст диплома");
let printLink = template.getCellValue("Ссылка на печать диплома");

console.log(program.getCellValue("Start date"), startDate);
console.log(program.getCellValue("End date"), endDate);

// Проверка данных
let missingFields = [];
if (!participantName) missingFields.push("Имя участника");
if (!diplomaText) missingFields.push("Текст диплома");
if (!printLink) missingFields.push("Ссылка на печать диплома");
if (!dateRange) missingFields.push("Дата начала и окончания программы (Start date / End date)");
if (!endDate) missingFields.push("End date");
if (!participantNumber) missingFields.push("Номер в группе");
if (!participantGroup) missingFields.push("Группа");

if (missingFields.length > 0) {
    console.log("Ошибка: Не заполнены следующие поля:\n" + missingFields.join(", "));
    return;
}

// Формируем данные
if (diplomaText && dateRange) {
    diplomaText = diplomaText.replace("[dateRange]", dateRange);
}

let certificateNumber;
let participantGroupName = participantGroup[0].name;
if (participantGroupName && participantNumber) {
    certificateNumber = "Certificate number: " + generateCertificateNumber(participantGroupName, participantNumber);
}

// Генерируем URL
let queryParams = encodeQueryParams({
    participantName: participantName,
    diplomaText: diplomaText,
    date: endDate || "",
    certificateNumber: certificateNumber || ""
});

let finalUrl = `${printLink}?${queryParams}`;

// Обновляем запись
await participants.updateRecordAsync(record.id, {
    "Print diploma link": finalUrl,
    "Diploma link updated": new Date()
});

console.log("✅ Link to diploma is updated!");
