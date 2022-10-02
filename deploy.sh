# !/bin/bash

ZIP_FUNCTION_FILE="./.deploy.zip"

FUNCTION_NAME=happy-birthday
# имя функции

ENTRYPOINT=main.handler
# обработчик, указывается в формате файла с функцией обработчика <имя >.<имя >

RUNTIME=python38
# среда выполнения

MEMORY=128m
# объем RAM

TIMEOUT=10s
# максимальное время выполнения функции до таймаута

# lockbox
function lockbox() { yc lockbox payload get "${1}" --key "${2}"; }

TELEGRAM_TOKEN=$(lockbox ${FUNCTION_NAME} TELEGRAM_TOKEN)

YDB_ENDPOINT=$(lockbox ${FUNCTION_NAME} YDB_ENDPOINT)
YDB_ACCESS_KEY_ID=$(lockbox ${FUNCTION_NAME} YDB_ACCESS_KEY_ID)
YDB_ACCESS_KEY_SECRET=$(lockbox ${FUNCTION_NAME} YDB_ACCESS_KEY_SECRET)

rm -rf "${ZIP_FUNCTION_FILE}"

zip -r "${ZIP_FUNCTION_FILE}" ./ -x "deploy.sh"

yc serverless function version create \
  --function-name=${FUNCTION_NAME} \
  --runtime ${RUNTIME} \
  --entrypoint ${ENTRYPOINT} \
  --memory ${MEMORY} \
  --execution-timeout ${TIMEOUT} \
  --environment "TELEGRAM_TOKEN=${TELEGRAM_TOKEN}" \
  --environment "YDB_ENDPOINT=${YDB_ENDPOINT}" \
  --environment "YDB_ACCESS_KEY_ID=${YDB_ACCESS_KEY_ID}" \
  --environment "YDB_ACCESS_KEY_SECRET=${YDB_ACCESS_KEY_SECRET}" \
  --source-path "${ZIP_FUNCTION_FILE}" | # zip-архив c кодом функции и всеми необходимыми зависимостями
  sed '1,/environment:/!d'               # очистка environment переменных при выводе

rm -rf "${ZIP_FUNCTION_FILE}"

YC_FUNCTION_ID=$(yc serverless function get "${FUNCTION_NAME}" --format json | jq -r '.id')
if [ ! -z "${YC_FUNCTION_ID}" ]; then
  YC_FUNCTION_ENDPOINT="https://functions.yandexcloud.net/${YC_FUNCTION_ID}"

  curl -s https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=${YC_FUNCTION_ENDPOINT}
fi
