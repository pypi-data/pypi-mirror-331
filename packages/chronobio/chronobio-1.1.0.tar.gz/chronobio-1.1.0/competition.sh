SKIP_UPDATE=$1

PORT=$(python -c "import random; print(random.randint(2000, 3000))")
echo "La compétition se passe sur 127.0.0.1:$PORT"

python -m chronobio.killall
find . -name "*.log" -exec rm \{} \;

if [ -z "$SKIP_UPDATE" ]
then
    for team in `ls teams`
    do
        echo "#################"
        echo "Updating $team"
        cd teams/$team
        git pull
        cd -
    done
fi

python -m chronobio.game.server -p $PORT --fast &
python -m chronobio.viewer -p $PORT &
sleep 2

for team in `ls teams`
do
    echo "#################"
    echo "Starting $team"
    cd teams/$team
    touch TROLLED
    ./_launch.sh $PORT >/dev/null 2>/dev/null &
    cd -
done

sleep 3600
python -m chronobio.killall
