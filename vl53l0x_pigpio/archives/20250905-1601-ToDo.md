# ToDo.md

## 優先事項

- [x] 測定はできるが、誤差が6cmもあるので、対策を検討する。
- [x] キャリブレーション機能を追加する。
- [x] キャリブレーションのオフセット値をファイルに保存し、VL53L0Xクラスは、設定ファイルが存在する場合には、自動的に読み込み、オフセット値を設定するようにしたい。
- [x] `uv run python -m pytest -v tests`を実行して、必要に応じて修正する。
- [x] `uv run vl53l0x_pigpio`を実行すると、以下のエラーが出るので、修正する。
```
Traceback (most recent call last):
  File "/home/ytani/work/vl53l0x_pigpio/.venv/bin/vl53l0x_pigpio", line 10, in <module>
    sys.exit(cli())
             ~~~^^
  File "/home/ytani/work/vl53l0x_pigpio/.venv/lib/python3.13/site-packages/click/core.py", line 1442, in __call__
    return self.main(*args, **kwargs)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/home/ytani/work/vl53l0x_pigpio/.venv/lib/python3.13/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
  File "/home/ytani/work/vl53l0x_pigpio/.venv/lib/python3.13/site-packages/click/core.py", line 1830, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
                           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "/home/ytani/work/vl53l0x_pigpio/.venv/lib/python3.13/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ytani/work/vl53l0x_pigpio/.venv/lib/python3.13/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
  File "/home/ytani/work/vl53l0x_pigpio/.venv/lib/python3.13/site-packages/click/decorators.py", line 34, in new_func
    return f(get_current_context(), *args, **kwargs)
  File "/home/ytani/work/vl53l0x_pigpio/src/vl53l0x_pigpio/__main__.py", line 166, in calibrate
    save_config(output_file, config_data)
    ^^^^^^^^^^^
NameError: name 'save_config' is not defined
```