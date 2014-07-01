#!/usr/bin/perl -w
$|=1 ;

use strict ;
use warnings;
use Getopt::Long;
use utf8;
use Unicode::Normalize;

binmode(STDOUT, ":utf8");
binmode(STDERR, ":utf8");

Getopt::Long::Configure(qw{no_auto_abbrev no_ignore_case_always});

my $use_regexp;
my $search=undef;
my $replace=undef;
my $simulate=0;
my $confirm=0;
my $extract_map=0;
my $apply_map=0;
my $debug=0;
my $help=0;
my $ignorecase=0;

GetOptions ('search|s=s' => sub { $use_regexp=0; $search=$_[1] },
	    'search-regex|S=s' => sub { $use_regexp=1; $search=$_[1] },
	    'replace|r=s' => \$replace,
	    'ignore-case|i' => \$ignorecase,
	    'simulate|t' => \$simulate,
	    'confirm|c' => \$confirm,
	    'extract-map|e' => \$extract_map,
	    'apply-map|a' => \$apply_map,
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
             -i, --ignore-case    search ingoring case
             -a, --apply-map      use a map to perform replacement
             -t, --simulate       perform a simulation for replacements
                                  the results will be displayed on standart output
             -c, --confirm        prompt before applaying replacements on files
                                  
        
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

error(1,"setting option --simulate makes no sense with option --extract-map") if ($extract_map && $simulate);
error(1,"setting option --confirm makes no sense with option --extract-map") if ($extract_map && $confirm);
error(1,"--extract-map and --apply-map option are mutually exclusives") if ($extract_map && $apply_map);
error(1,"setting option --extract-map implies to set options --search and --replace") if ($extract_map && ((not defined $search) || (not defined $replace)));

if (@ARGV == 0) {
    push(@ARGV, '-');
}

if ($use_regexp) {
    $replace = '"' . $replace . '"';
} else {
    $search = quotemeta($search);
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
    $s =~ s{([^a-zA-Z]?)([A-Z]*)([A-Z])([a-z]?)}{
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

    if ($match =~ /^[A-Z_0-9]+$/) {
	return id(uc(deaccent($repl)));
    } elsif ($match =~ /^[a-z_0-9]+$/) {
	return id(lc(deaccent($repl)));
    } elsif (($match eq camelize($match)) && (word_count(decamelize($match))>=2)) {
	return camelize($repl);
    } elsif ($match eq lc($match)) {
	return "#3#".lc($repl);
    } elsif ($match eq uc($match)) {
	return "#4#".uc($repl);
    } elsif ($match eq titleize($match)) {
	return "#5#".titleize($repl);
    } elsif ($match eq lcfirst($match)) {
	return "#6#".lcfirst($repl);
    } elsif ($match eq ucfirst($match)) {
	return "#7#".ucfirst($repl);
    } elsif ($match eq $search) {
	return "#8#".$repl;
    } 
    return "";
}

my $extracted = {};
sub extract($) {
    my ($fin) = @_;
    while (defined (my $line = <$fin>)) {
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
		$extracted->{$match} = compute_case($match,$search,$repl);
	    }
	}
    }
}

sub display_extracted {
    foreach my $k (keys(%$extracted)) {
	printf "$k: $extracted->{$k}\n"
    }
}

foreach my $file (@ARGV) {
    my $fdin;
    if (-d $file) {
	next;
    }
    if ($file eq '-') {
	$fdin = \*STDIN;
    } else {
	open(FILE,"$file") || die("Unable to open file '$file' ($!)\n") ;
	$fdin = \*FILE;
    }
    if ($extract_map) {
	extract($fdin);
    } else {
	die("Operation not supported");
    }
    if (fileno($fdin) != fileno(STDIN)) {
	close($fdin);
    }
}

if ($extract_map) {
    display_extracted;
    exit 0;
}
