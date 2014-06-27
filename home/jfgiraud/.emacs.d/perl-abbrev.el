(require 'stringtools)
(require 'abbrevtools)

(setq perl-abbrev-list
  (list
     (cons "p-w" "#!/usr/bin/perl -w\n\nuse strict;\n\n|")
     (cons "sub" "sub |{\n}")
     (cons "if" "if (|) {\n}")
     (cons "ifndef" "if (not defined |) {\n}")
     (cons "ife" "if (|) {\n} else {\n}")
     (cons "def" "defined ")
     (cons "ndef" "not defined ")
     (cons "@_" "my (|) = @_;")
     (cons "ret" "return |")
   )
)

(setq perl-backward-separator
      '("	" " " "."))

(setq perl-abbrev-list (reverse (sort perl-abbrev-list 'sort-fct)))


(defun perl-expand-abbrev ()
   (interactive)
   (expand-abbrev perl-abbrev-list)
)

(local-set-key [?\e ?j]  'perl-expand-abbrev)

(provide 'perl-abbrev)





