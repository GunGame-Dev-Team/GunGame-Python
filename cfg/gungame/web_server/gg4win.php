<?php
// This file controls the default behavior if gg_winner_display is set to zero.
//
// Enter the IP or domain of your game server's ftp
$serverip = "localhost";
// Enter the path to your cstrike directory including a trailing slash
$basepath = "/home/";
// Enter the ftp username
$username = "username";
// Enter the ftp password
$password = "password";
// Enter the ftp port(usually 21)
$port = '21';
// Enter the url of the image you want at the top of the page including the " at each end
$image = 'images/ggv4.gif';
// Image attributes
$image_attr = 'width="700" height="100"';
// -------------------  do not modify below this line ----------------------------------
header('Content-type: text/html; charset=utf-8');
?>
<HTML>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<HEAD>
<TITLE>:::GunGame4 SQL Lite Database Structure:::</TITLE>
<? echo '<link rel=stylesheet type="text/css" href="'.$address.'motd.css">'; ?>
</HEAD>
<BODY>
<?
$filepath = $basepath."cstrike/addons/eventscripts/gungame4/addons/web_data/es_gg4wins_db.txt";
$local_file = 'es_gg4wins_db.txt';
if (file_exists($local_file)) {
$lasttransfer = filemtime($local_file);
$elapsed = time() - $lasttransfer;
}
else
{
$elapsed = 200;
}
if ($elapsed > 120) {
$ftp = ftp_connect($serverip, $port, 15);
ftp_login($ftp, $username, $password);
ftp_get($ftp, $local_file, $filepath, FTP_ASCII);
} 

$fp = fopen($local_file, "r");
$index = 0;
while(!feof($fp)) {
$records[$index] = fgets($fp, 1024);
$index++;
}

$playername = get_data($records, '"name"');
$playerlevel = get_data($records, '"level"');
$playerkills = get_data($records, '"kills"');
$playerdeaths = get_data($records, '"deaths"');
$playerwins = get_data($records, '"wins"');
$playerrank = get_data($records, '"rank"');
$temp = get_data($records, '"winner"');
$winner = $temp[0];
$temp = get_data($records, '"winnerwins"');
$wins = $temp[0];
$temp = get_data($records, '"winnerrank"');
$rank = $temp[0];
$temp = get_data($records, '"loser"');
$loser = $temp[0];
$temp = get_data($records, '"totals"');
$totals = $temp[0];
echo '<div align="center">';
if ($image)
    if ($image_attr)
        echo '<img src="'.$image.'" '.$image_attr.'>';
    else
        echo '<img src="'.$image.'">';
echo '</div><br /><p class="style4"><span class="style6">'.$winner.'</span> has won the round by killing <span class="style11">'.$loser.'</span>';
echo '<br />';
echo 'Congratulations '.$winner.'!! </p>';
echo '<p class="style4"><span class="style6">'.$winner."'s stats</span>";
echo "     Wins: ".$wins."<br>";
echo "     Rank: ".$rank."/".$totals;

?>
<table border="10" bordercolorlight="black" bordercolordark="gray" width="100%">
<caption><h1>GunGame4 Round Results:</h1></caption>
<tr>
<th BGCOLOR="red">Player</th>
<th BGCOLOR="red">Level</th>
<th BGCOLOR="red">Kills</th>
<th BGCOLOR="red">Deaths</th>
<th BGCOLOR="red">Wins</th>
<th BGCOLOR="red">Rank</th>
</tr>
<?
for($index = 0; $index < count($playername); $index++) {
echo "<tr>\n";
echo '<td ALIGN=center><span class="style4">'.$playername[$index]."</span></td>";
echo '<td ALIGN=center><span class="style4">'.$playerlevel[$index]."</span></td>";
echo '<td ALIGN=center><span class="style4">'.$playerkills[$index]."</span></td>";
echo '<td ALIGN=center><span class="style4">'.$playerdeaths[$index]."</span></td>";
echo '<td ALIGN=center><span class="style4">'.$playerwins[$index]."</span></td>";
echo '<td ALIGN=center><span class="style4">'.$playerrank[$index]."</span></td>";
echo "</tr>\n";
};
?>
</table>
</BODY>
</HTML>
<?

function get_data($records, $id) {
	$counter = 0;
	for ($index = 1; $index < count($records); $index++) {
		if (strstr($records[$index], $id)) {
			$temparray[$counter] = get_value($records[$index]);
			$counter++;
		}
	}
	return $temparray;
}

function get_value($line) {
    $line = str_replace('"', '', $line);
    $line = trim($line, " ");
    $line = trim($line, "\t");
    $line = trim($line, "\n");
    $line = substr($line, strpos($line, "\t"));
    return $line;
}


function find_key1($record) {
$index = 0;
while (!strstr($record[$index],"}")) {
$index++;
}
$index++;
return $index;
}
