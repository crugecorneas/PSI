#!/bin/bash

# Verifica si se pasó el mensaje de commit como argumento
if [ -z "$1" ]; then
    echo "Por favor, proporciona un mensaje de commit."
    exit 1
fi

# Verifica si se pasó el usuario a configurar
while getopts "IJ" opt; do
    case ${opt} in
        I)
            # Configura los datos de usuario para Iñaki
            git config --global user.email "innaki.delafuente@estudidante.uam.es"
            git config --global user.name "Iñaki"
            echo "Configuración de usuario: Iñaki"
            ;;
        J)
            # Configura los datos de usuario para Freddy
            git config --global user.email "freddy.serrano.zurita@gmail.com"
            git config --global user.name "Freddy Serrano Zurita"
            echo "Configuración de usuario: Freddy Serrano Zurita"
            ;;
        *)
            echo "Opción no válida. Usa -I para Iñaki o -J para Freddy."
            exit 1
            ;;
    esac
done

# Agrega todos los cambios
git add .

# Realiza el commit con el mensaje proporcionado
git commit -m "$1"

# Realiza el push al repositorio remoto
git push

# Mensaje de éxito
echo "Cambios enviados con éxito con el mensaje: $1"
