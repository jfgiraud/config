;;;======================================================================
;;; Fonctions sur les chaines de caractères
;;;======================================================================

(defun is-space(c)
  (or (= c (string-to-char " "))
      (= c (string-to-char "\t"))
      (= c (string-to-char "\n"))
      (= c (string-to-char "\r"))
      ))

(defun lstrip(s)
  (if (and s (> (length s) 0) (is-space (string-to-char s)))
      (lstrip (substring s 1))
    s))

(defun rstrip(s)
  (if (and s (> (length s) 0) (is-space (string-to-char (substring s -1))))
      (rstrip (substring s 0 -1))
    s))

(defun strip(s)
  (rstrip (lstrip s)))

(defun string-reverse (s)
  (if (and s (>= (length s) 0))
      (concat (reverse (string-to-list s)))
    nil))

(defun zap-to(s c)
  (if (and s (> (length s) 0) (not (string= (substring s 0 1) c)))
      (zap-to (substring s 1) c)
    s))

(defun index-of (subst s)
  (if (string-match subst s)
      (string-match subst s)
    nil))

(defun last-index-of (subst s)
  (if (index-of 
       (string-reverse subst) 
       (string-reverse s))
      (- (length s)
	 (index-of 
	  (string-reverse subst) 
	  (string-reverse s)))
    nil))

(defun ends-with (s ew)
   (if (> (length ew) (length s))
       nil
       (let ((e (substring s (- (length ew)) (length s))))
	    (message e)
	    (string= e ew))))

(provide 'stringtools)
