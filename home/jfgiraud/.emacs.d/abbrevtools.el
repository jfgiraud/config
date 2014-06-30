(defun sort-fct (x y)
  (let ((a (car x))
	(b (car y)))
  (if (= (length a) (length b))
      (string< a b)
    (< (length a) (length b)))))

(defun search (l v)
   (if (not l)
       nil
       (if (string= (car (car l)) v)
	   (cdr (car l))
	 (search (cdr l) v))))

(defun get-identifier (string list)
  (if (not list)
      nil
    (if (ends-with string (car list))
	(car list)
      (get-identifier string (cdr list)))))

(defun insert-expansion (beg end str cur)
   (goto-char beg)
   (delete-region beg end)
   (insert str)
   (indent-region beg (point) nil)
   (if (search-backward cur beg t)
      (delete-char 1))
   (point))

(defun expand-abbrev (liste)
   (let ((pos (point)))
      (save-excursion
	 (beginning-of-line)
         (let* ((end pos)
		(beg (point))
		(debut (buffer-substring beg end))
		(id (get-identifier debut (mapcar '(lambda (l) (car l)) liste))))
	   (if id
	       (setq pos
		     (insert-expansion (- end (length id))
				       end (search liste id) "|"))
  	       (error "Abbrev not found."))))
      (goto-char pos)
      ))

(provide 'abbrevtools)
