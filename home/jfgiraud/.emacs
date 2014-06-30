;; This buffer is for notes you don't want to save, and for Lisp evaluation.
;; If you want to create a file, visit that file with C-x C-f,
;; then enter the text in that file's own buffer.
(add-to-list 'load-path "~/.emacs.d/")
(add-to-list 'load-path "~/.emacs.d/color-theme/")
(require 'color-theme)
(load-file "~/.emacs.d/themes/color-theme-blackboard.el")
(color-theme-blackboard) 

(menu-bar-mode -1)
(tool-bar-mode -1)
(scroll-bar-mode -1)

(set-default-font "7x13")

(setq column-number-mode t)
(setq line-number-mode t)
(setq inhibit-startup-message t)

;; ==================== KEYS ====================
;; already bind via simple.el
;; (global-set-key [home] 'beginning-of-line)
;; (global-set-key [end] 'end-of-line) 
;; (global-set-key [backspace] 'backward-delete-char-untabify)
;; (global-set-key [(control space)] 'set-mark-command)
;; (global-set-key [(control insert)] 'kill-ring-save)
;; (global-set-key [(shift insert)] 'yank)
;; (global-set-key [(control home)] 'beginning-of-buffer)
;; (global-set-key [(control end)] 'end-of-buffer)
;; (global-set-key [(control left)] 'backward-word)
;; (global-set-key [(control right)] 'forward-word)
;; (global-set-key [(control o)] 'open-line)

;; already bind via paragraphs.el
;; (global-set-key [(control down)] 'forward-paragraph)
;; (global-set-key [(control up)] 'backward-paragraph)


(defun beginning-of-page () (interactive) (move-to-window-line 0))
(defun end-of-page () (interactive) (move-to-window-line -1))
(global-set-key [(control kp-begin)] 'move-to-window-line)
(global-set-key [(control kp-down)] 'end-of-page)
(global-set-key [(control kp-up)] 'beginning-of-page)

(defun delete-char-or-region() (interactive) (if mark-active (delete-region (point) (mark)) (delete-char 1)))
(global-set-key [delete] 'delete-char-or-region)

(global-set-key [(control return)] 'newline-and-indent)
(global-set-key [(control delete)] 'kill-region)


(global-set-key [?\e ?s] 'point-to-register)  ;; M-s
(global-set-key [?\e ?r] 'jump-to-register) ;;  M-r


(global-set-key [?\e backspace] 'backward-kill-word)
(global-set-key [?\e delete] 'kill-word)

(global-set-key [?\e ?g] 'goto-line)

(global-set-key [M-return] 'kill-this-buffer)
(global-set-key [(control >)]    'bs-cycle-next)
(global-set-key [(control <)]   'bs-cycle-previous)
(global-set-key [f5]     'linum-mode)
(global-set-key [f6]     'menu-bar-mode)
(global-set-key [f8]     'next-error)
(global-set-key [f9]     'compile) ;;my-compile-or-tramp-compile)


(defun move-region (start end n)
  "Move the current region up or down by N lines."
  (interactive "r\np")
  (let ((line-text (delete-and-extract-region start end)))
    (forward-line n)
    (let ((start (point)))
      (insert line-text)
      (setq deactivate-mark nil)
      (set-mark start))))

(defun move-region-up (start end n)
  "Move the current line up by N lines."
  (interactive "r\np")
  (move-region start end (if (null n) -1 (- n))))

(defun move-region-down (start end n)
  "Move the current line down by N lines."
  (interactive "r\np")
  (move-region start end (if (null n) 1 n)))

(defun move-line (n)
  "Move the current line up or down by N lines."
  (interactive "p")
  (setq col (current-column))
  (beginning-of-line) (setq start (point))
  (end-of-line) (forward-char) (setq end (point))
  (let ((line-text (delete-and-extract-region start end)))
    (forward-line n)
    (insert line-text)
    ;; restore point to original column in moved line
    (forward-line -1)
    (forward-char col)))

(defun move-line-up (n)
  "Move the current line up by N lines."
  (interactive "p")
  (move-line (if (null n) -1 (- n))))

(defun move-line-down (n)
  "Move the current line down by N lines."
  (interactive "p")
  (move-line (if (null n) 1 n)))

(defun move-line-region-up (start end n)
  (interactive "r\np")
  (if (region-active-p) (move-region-up start end n) (move-line-up n)))

(defun move-line-region-down (start end n)
  (interactive "r\np")
  (if (region-active-p) (move-region-down start end n) (move-line-down n)))

(global-set-key [(meta up)] 'move-line-region-up)
(global-set-key [(meta down)] 'move-line-region-down)


;;; Déplacements entre buffers ************************************************
;;; Affichage du nom du fichier dans minibuffer *******************************

(global-set-key [(meta left)]    'goto-previous-buffer)
(global-set-key [(meta right)]   'goto-next-buffer)

(defun goto-next-buffer ()
  ""
  (interactive)
  (let ((l (reverse (buffer-list)))
        (buf (current-buffer))
        (regexp "^ ?\\*.*\\*$")
        )
    (while (progn
             (if l nil
               (switch-to-buffer buf)
               (error "No buffer to show"))
             (switch-to-buffer (car l))
             (message (buffer-file-name))
             (setq l (cdr l))
             (string-match regexp (buffer-name (current-buffer)))))))

(defun goto-previous-buffer ()
  ""
  (interactive)
  (let ((n (length (buffer-list)))
        (k 0)
        (buf (current-buffer))
        (regexp "^ ?\\*.*\\*$")
        )
    (while (progn
             (setq k (1+ k))
             (if (<= k n) nil
               (switch-to-buffer buf)
               (error "No buffer to show"))
             (bury-buffer)
             (message (buffer-file-name))
             (string-match regexp (buffer-name (current-buffer)))))))

;;; deplacement entre frames **************************************************

(global-set-key (kbd "<c-s-iso-lefttab>")
  '(lambda () (interactive)
     (message (buffer-file-name)) (other-window -1)))
(global-set-key [(control tab)]
  '(lambda () (interactive)
     (message (buffer-file-name)) (other-window 1)))

;;; Acces par REGEXP dans C-x b ***********************************************

(iswitchb-mode t)
;(iswitchb-default-keybindings)

(defun iswitchb-system-buffers-to-end ()
  ""
  (let ((files (delq nil (mapcar 
                          (lambda (x) 
                            (if (or 
                                 (string-match "Summary" x)
                                 (string-match "^ ?\\*.*\\*$" x))
                                x))
                          iswitchb-temp-buflist))))
    (iswitchb-to-end files)))

(add-hook 'iswitchb-make-buflist-hook 'iswitchb-system-buffers-to-end)


;;; Mode abbrev ***************************************************************

(add-hook 'perl-mode-hook                         
  (function
   (lambda ()
     ; faire en sorte que le _ appartienne au mot
     ; pour les abbréviations
     (require 'perl-abbrev))))

(message "main is loaded")
