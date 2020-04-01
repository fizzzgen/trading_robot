# Trading robot
### Система:
- ##### Predict pipeline (job_predict.py)
  - Предсказание раз в N минут
  - Создание ордера на buy, добавление ордера в таблицу transactions со статусом TO_ENQUEUE
- ##### Order engine pipeline (job_order_engine.py)
  - Создание ордеров на BUY
  - Удержание ордеров на BUY/SELL(ON_STOP) на вершине стэка
  - Отмена ордеров на BUY по тайм-стопу
  - Создание ордеров на SELL по рэйт-стопу, от выполненных транзакций на BUY
  - Перевод SELL ордеров по тайм-стопу в статус ON_STOP
- ##### Price update pipeline (job_price_update.py)
  - обновление информации о текущих стэках в таблице price

Скрипты для надежности запускаются как systemctl сервисы (соответствующие файлы находятся в services/)

- ##### Buy transaction status pipeline:
   - TO_ENQUEUE -> ENQUEUED -> CANCELLED (time-stop)/COMPLETED , созданы trades в соотв таблице
- ##### Sell transaction pipeline:
   - ENQUEUED(проставлен фикс на рэйт-стоп) -> (ON_STOP если превысила таймстоп, цена начинает быть на вершине стэка) -> COMPLETED, созданы trades в соотв таблице

#### Конфигурация:
Отредактировать conf/config.py, проставить полные пути до файлов.
Проставить полные пути до скриптов в файлах services/*.service
Переместить файлы *.service в соответствующую директорию System.D

#### Запуск:
sudo systemctl *.service start (Для каждого отдельно)
