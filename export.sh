for i in $(find . | grep -E "(web_ui.py|.css|.html|test_web_ui.py)");
do
    echo $i
    cat $i
    echo
    echo
done > all-code.txt

echo >> all-code.txt
echo >> all-code.txt

tree . >> all-code.txt
