#!/usr/bin/perl -w
$|=1 ;

use strict ;
use warnings;
use Getopt::Long;
use utf8;
use Unicode::Normalize;

#binmode(STDOUT, ":utf8");
#binmode(STDERR, ":utf8");

Getopt::Long::Configure(qw{no_auto_abbrev no_ignore_case_always});

my $tmp_name = ".bak";
my $use_regexp;
my $search=undef;
my $replace=undef;
my $simulate=0;
my $color=0;
my $extract_map=0;
my $apply_map=0;
my $map_file=undef;
my $debug=0;
my $help=0;
my $ignorecase=0;
my $algorithm = undef;
my $algorithms = { 'id' => \&compute_id,
		   'keep' => \&compute_case,
		   'default_direct' => undef, 
		   'default_extract' => \&compute_case
};

GetOptions ('search|s=s' => sub { $use_regexp=0; $search=$_[1] },
	    'search-regex|S=s' => sub { $use_regexp=1; $search=$_[1] },
	    'replace|r=s' => \$replace,
	    'ignore-case|i' => \$ignorecase,
	    'simulate|t' => \$simulate,
	    'color|c' => \$color,
	    'extract-map|e' => \$extract_map,
	    'compute-case-method|m=s' => \$algorithm,
	    'apply-map|a=s' => sub { $apply_map=1; $map_file=$_[1] },
	    'help|h' => \$help,
	    'debug|d' => \$debug
);

sub error($$) {
    my ($status, $msg) = @_;
    print STDERR "$msg\n";
    exit($status);
}

sub usage {
    my $prog = $0; 
    $prog =~ s/.*\///g;
    print STDERR <<EOF;
NAME:

        $prog - perform pattern replacement in files

SYNOPSYS:

        $prog
             -h, --help           display help
             -s, --search         the string to search
             -S, --search-regex   the pattern to search
             -r, --replace        the string (or the pattern) used to replace all matches 
             -e, --extract-map    extract from file or standart input all matches of searched
                                  string or pattern.
                                  a map created with found matches is displayed on standart 
                                  output. entries of this map will be setted with a default
                                  value
 *********************************************
fdout non gere
 *********************************************

             -i, --ignore-case    search ingoring case
             -a, --apply-map      use a map to perform replacement
             -t, --simulate       perform a simulation for replacements
                                  the results will be displayed on standart output
             -c, --color          perform a simulation for replacements
                                  the results will be displayed on standart output
                                  colorize modified lines 
                                  
        
With no FILE, or when FILE is -, read standard input.

AUTHOR
	Written by Jean-Francois Giraud.

COPYRIGHT
	Copyright (c) 2012-2014 Jean-François Giraud.  
	License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
	This is free software: you are free to change and redistribute it.  
	There is NO WARRANTY, to the extent permitted by law.

EOF

}

if ($help) {
    usage 
}

if ($debug) {
    print STDERR "search: $search" . ($use_regexp ? " (regex)" : " (fixed)") . "\n";
    print STDERR "replace: $replace\n";
    print STDERR "simulate: $simulate\n";
}

$simulate=1 if $color;

error(1,"setting option --simulate makes no sense with option --extract-map") if ($extract_map && $simulate);
error(1,"--extract-map and --apply-map option are mutually exclusives") if ($extract_map && $apply_map);
error(1,"setting option --extract-map implies to set options --search and --replace") if ($extract_map && ((not defined $search) || (not defined $replace)));
error(1,"--search and --replace are required when --apply-map is not used") if ((not $apply_map) && ((not defined $search) || (not defined $replace)));
error(1,"unknown algorithm '$algorithm' for option --compute-case-method") if ((defined $algorithm) && not exists ($algorithms->{$algorithm}));

if (0) {
    sub assert($$$$) {
	my ($expect, $match, $search, $replace) = @_;
	my $actual = compute_case($match, $search, $replace);
	if ($expect ne $actual) {
	    if (not defined $search) {
		$search="";
	    }
	    printf STDERR "Expects      <$expect>\nBut receives <$actual>\nFor <$match> <$search> <$replace>\n";
	    exit 1;
	}
    }
    assert('REP_LACE_33', 'SEA_RCH', undef, 'rép läce 33');
    assert('rep_lace_33', 'sea_rch', undef, 'rép läce 33');
    assert('rep_lace_33', 'sea_rch', undef, 'rep_lace_33');
    assert('REP_LACE_33', 'SEA_RCH', undef, 'RépLäce33');
    assert('New', 'Old', undef, 'new');
    assert('New word', 'Old', undef, 'new word');
    assert('New', 'Old', undef, 'New');
    assert('New', 'Old', undef, 'NEW');
    assert('NEW', 'OLD', undef, 'new');
    assert('NEW', 'OLD', undef, 'New');
    assert('NEW', 'OLD', undef, 'NEW');
    assert('The New Sentence', 'The Old Sentence', undef, 'The new sentence');
    assert('The New Sentence', 'The Old Sentence 33', undef, 'The new sentence');
    assert('The new sentence', 'The old sentence', undef, 'The New sentence');
    assert('The new séntence', 'The old sentence', undef, 'The New séntence');
    assert('THE NEW SÉNTENCE', 'THE OLD SENTENCE', undef, 'The New séntence');
    assert('THE NEW SÉNTENCE', 'THE OLD SENTENCE', undef, 'The New SÉNTENCE');
    assert('The new sentence', 'The OLD sentence', undef, 'The New sentence');
    assert('the new sentence', 'the OLD sentence', undef, 'The New sentence');
    assert('The New sentence', 'the OLD sentence', 'the OLD sentence', 'The New sentence');
    exit 0;
}

if (@ARGV == 0) {
    push(@ARGV, '-');
}

if (not $apply_map) {
    if ($use_regexp) {
	$replace = '"' . $replace . '"';
    } else {
	$search = quotemeta($search);
    }
    if (not defined $algorithm) {
	if ($ignorecase) {
	    $algorithm = 'keep';
	} else {
	    $algorithm = 'id';
	}
    }
    #print "<$algorithm>\n";
}


sub deaccent($) {
    my ($s) = @_;
    $s = NFD($s);
    $s =~ s/\p{Mn}//g;
    return $s;
}

sub id($) {
    my ($s) = @_;
    $s =~ y/ /_/s;
    return $s;
}

sub camelize($) {
    my ($s) = @_;
    return join('', map{ ucfirst $_ } split(/(?<=[A-Za-z])_(?=[A-Za-z])|\b|\s/, $s));
}

sub decamelize($) {
    my ($s) = @_;
    $s =~ s{([^a-zA-Z0-9]?)([A-Z0-9]*)([A-Z0-9])([a-z]?)}{
		my $fc = pos($s)==0;
		my ($p0,$p1,$p2,$p3) = ($1,lc$2,lc$3,$4);
		my $t = $p0 || $fc ? $p0 : '_';
		$t .= $p3 ? $p1 ? "${p1}_$p2$p3" : "$p2$p3" : "$p1$p2";
		$t;
	}ge;
    return $s;
}

sub titleize($) {
    my $s = shift;
    $s =~ s/(\w+)/\u\L$1/g;
    return $s;
}

sub word_count($) {
    my ($s) = @_;
    $s =~ s/_/ /g;
    my $c = 0;
    ++$c while ($s =~ /\S+/g);
    return $c;
}

sub compute_case($$$) {
    my ($match, $search, $repl) = @_;
    if ((defined $search) && ($search eq $match)) {
	return $repl;
    }
    if ($match =~ /_/) {
	my $repl2 = $repl;
	if (($repl2 eq camelize($repl2)) && (word_count(decamelize($repl2))>=2)) {
	    $repl2 = decamelize($repl2);
	}
	if ($match =~ /^[A-Z_0-9]+$/) {
	    return id(uc(deaccent($repl2)));
	} elsif ($match =~ /^[a-z_0-9]+$/) {
	    return id(lc(deaccent($repl2)));
	} 
    } 
    if ($match eq lc($match)) {
	return lc($repl);
    }
    if ($match eq uc($match)) {
	return uc($repl);
    }
    if (word_count($match) >= 2 && $match eq titleize($match)) {
        return titleize($repl);
    }
    if ($match =~ /^[A-Z]/) {
	return ucfirst(lc($repl));
    }
    if ($match =~ /^[a-z]/) {
	return lc($repl);
    }
    return $repl;
}

sub compute_id($$$) {
    my ($match, $search, $repl) = @_;
    return $repl;
}

my $extracted = {};
sub extract($) {
    my ($fdin) = @_;
    my $function = exists($algorithms->{$algorithm}) ? $algorithms->{$algorithm} : $algorithms->{"default_extract"}; 
    while (defined (my $line = <$fdin>)) {
	my @table;
	if ($ignorecase) {
	    while ($line =~ /($search)/gi) {
		push(@table,"$1");
	    }
	} else {
	    while ($line =~ /($search)/g) {
		push(@table,"$1");
	    }
	}
	foreach my $match (@table) {
	    if (not exists $extracted->{$match}) {
		my $repl = $match;
		if ($use_regexp) {
		    if ($ignorecase) {
			$repl =~ s/$search/$replace/giee;
		    } else {
			$repl =~ s/$search/$replace/gee;
		    }
		} else {
		    $repl = $replace;
		}
		$extracted->{$match} = (defined $function ? &$function($match,$search,$repl) : "");
	    }
	}
    }
}

sub display_extracted {
    foreach my $k (keys(%$extracted)) {
	printf "$k => $extracted->{$k}\n"
    }
}

sub parse_file_to_map($) {
    my ($name) = @_;
    my $h = {};
    open(MAP,"<$name") || die("Unable to open file '$name' ($!)\n") ;
    while (defined (my $line = <MAP>)) {
	chomp($line);
	my ($k, $v) = split(/ => /, $line, 2);
	$h->{$k} = $v;
    }
    close(MAP);
    return $h;
} 

sub apply_map($$) {
    my ($fdin, $fdout) = @_;
    my $repl = parse_file_to_map("$map_file");
    my $regexp = "(" . join("|", reverse(sort(keys(%$repl)))) . ")";
    while (defined (my $line = <$fdin>)) {
	my $ori = $line;
        $line =~ s/$regexp/$repl->{$1}/g;
        if (fileno($fdout) == fileno(STDOUT)) {
            if ($color && ($line ne $ori)) {
		print $fdout "\033[0;31m$line\033[0;39m";
	    } else {
		print $fdout $line;
	    }
        } else {
            printf $fdout $line;
        }
    }
}

sub algo($$$) {
    my ($match, $search, $replace) = @_;
    my $function = exists($algorithms->{$algorithm}) ? $algorithms->{$algorithm} : $algorithms->{"default_direct"}; 
    return (defined $function ? &$function($match,$search,$replace) : $replace);
}

sub unquote($) {
   my ($s) = @_;
   $s =~ s/^"//;
   $s =~ s/"$//;
   return $s;
}

sub algox($$$) {
    my ($match, $search, $replace) = @_;
    return algo($match,$search,unquote($replace));
}

sub apply_repl($$) {
    my ($fdin, $fdout) = @_;
    my $rreplace = $replace;
    $rreplace = '"' . $rreplace . '"'; 
    while (defined (my $line = <$fdin>)) {
        my $ori = $line;
        if ($use_regexp) {
            if ($ignorecase) {
                $line =~ s/($search)/algox($1,$search,$rreplace)/geei;
	    } else {
	        $line =~ s/($search)/algox($1,$search,$rreplace)/gee;
	    }
        } else {
            if ($ignorecase) {
                $line =~ s/($search)/algo($1,$search,$replace)/gei;
	    } else {
                $line =~ s/($search)/algo($1,$search,$replace)/ge;
	    }
        }
        if (fileno($fdout) == fileno(STDOUT)) {
            if ($color && ($line ne $ori)) {
		print $fdout "\e[0;31m$line\e[0;39m";
	    } else {
		print $fdout $line;
	    }
        } else {
            printf $fdout $line;
        }
    }
}

sub displaybar($) {
    my ($title) = @_;
    my $separator;
    my $ncols = `tput cols`;
    if (length($title) == 0) {
	$separator = "-" x $ncols;
    } else {
	$separator = "-" x ($ncols - length($title) - 5);
    }
    if ($color) {
	printf STDERR "\e[0;32m-- $title $separator\e[0;39m\n";
    } else {
	printf STDERR "-- $title $separator\n";
    }
}

foreach my $file (@ARGV) {
    my $fdin;
    my $fdout;
    if (-d $file) {
	next;
    }
    if (@ARGV >= 2 && $simulate == 1) {
	displaybar($file);
    }
    if ($file eq '-') {
	$fdin = \*STDIN;
        $fdout = \*STDOUT;
    } else {
	open(FILE,"$file") || die("Unable to open file '$file' ($!)\n") ;
	$fdin = \*FILE;
        if ($simulate == 0) {
            open(TMPFILE,">$file.$tmp_name") || die("Unable to create the temporary file '$file.$tmp_name' ($!)\n") ;
            $fdout = \*TMPFILE;
        } else {
            $fdout = \*STDOUT;
        }
    }
    if ($extract_map) {
	extract($fdin);
    } elsif ($apply_map) {
	apply_map($fdin, $fdout);
    } elsif (defined $search && defined $replace) { 
        apply_repl($fdin, $fdout);
    } else {
	die("Operation not supported");
    }
    if (fileno($fdin) != fileno(STDIN)) {
	close($fdin);
    }
    

    if (fileno($fdout) != fileno(STDOUT)) {
        my @file_info = stat($file) ;
        close($fdout) ;
        unlink($file) || die("Unable to remove file '$file' ($!)\n") ;
        rename("$file.$tmp_name",$file) || die("Unable to remove temporary file '$file.$tmp_name' ($!)\n") ;
	chmod($file_info[2],$file) || die("Unable to restore permissions on file '$file' ($!)\n");
	chown($file_info[4],$file_info[5],$file) || die("Unable to restore file owner for '$file'\n");
    }
}

if ($extract_map) {
    display_extracted;
    exit 0;
}

