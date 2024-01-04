#!/bin/sh
pyuic5 -o ./fusebmc_ui_gen/MainWindow_.py ./fusebmc_ui/MainWindow.ui
pyuic5 -o ./fusebmc_ui_gen/DlgYaml_.py ./fusebmc_ui/DlgYaml.ui
echo "Done !!!"
