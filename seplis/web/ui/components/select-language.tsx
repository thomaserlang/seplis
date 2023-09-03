import { Select, SelectProps } from '@chakra-ui/react'
import { forwardRef, useMemo } from 'react'
import ISO6391 from 'iso-639-1'


// Extend the Select component
export const SelectLanguage = forwardRef<any, SelectProps>((props, ref) => {
    const languages = useMemo(() => {
        return <>{ISO6391.getLanguages(ISO6391.getAllCodes()).map((language) => {
            return <option key={language.code} value={language.code}>{language.name}</option>
            })}
        </>
    }, [])

    return <Select ref={ref} {...props} placeholder="Select a language">
        {languages}
    </Select>
})
