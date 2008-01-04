<?php
// This file controls the default behavior if gg_winner_display is set to zero.
//
// Enter the base web address where the motd.css is located, including the trailing slash
$address = 'http://www.yourwebsite.com/';
// Banner image to use
$image = 'http://www.yourwebsite.com/images/ggv4.gif';
// Image attributes
$image_attr = 'width="700" height="100"';
// -------------------  do not modify below this line ----------------------------------
header('Content-type: text/html; charset=utf-8');
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<? echo '<link rel=stylesheet type="text/css" href="'.$address.'motd.css">'; ?>
</head>
<body>
<?
if ($image)
	if ($image_attr)
		echo '<div align="center"><img src="'.$image.'" '.$image_attr.' /><br />';
	else
		echo '<div align="center"><img src="'.$image.'" /><br />';
?>
<span class="style1"><?php echo $_GET["winner"]; ?> won!!</span>
</div>
<hr>
<p class="style4"><span class="style11"><?php echo $_GET["winner"]; ?></span> has won the game by killing <span class="style6"><?php echo $_GET["loser"]; ?></span><br />
  Congratulations <span class="style11"><?php echo $_GET["winner"]; ?></span>!!
</p>
<br />
<hr color=#FF0000 width=60%>
<p class="style4"><span class="style7"><?php echo $_GET["winner"]; ?>'s Stats</span><br />
	Wins: <?php echo $_GET["wins"]; ?><br />
	Rank: <span class="style11"><?php echo $_GET["rank"]; ?></span> of <span class="style6"><?php echo $_GET["total"]; ?></span> ranked players.
</p>
</body>
</html>
