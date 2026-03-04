with open('test_app.jsonl', 'a', encoding='utf-8') as f:
    f.write('{"level": "ERROR", "message": "Failed 1"}\n')
    f.write('{"level": "ERROR", "message": "Failed 2"}\n')
    f.write('{"level": "ERROR", "message": "Failed 3"}\n')
    f.write('{"level": "ERROR", "message": "Failed 4"}\n')
